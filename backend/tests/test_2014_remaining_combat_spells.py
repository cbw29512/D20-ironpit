from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.dice import FixedDiceProvider
from app.combat.emanation_save_damage import resolve_emanation_hit
from app.combat.hit_points import effective_max_hp
from app.combat.modifier_stack import attack_roll_flat_bonus, effective_armor_class, saving_throw_flat_bonus, weapon_damage_flat_bonus
from app.combat.precombat_spells import prepare_defenses
from app.combat.restoration_riders import apply_hit_point_maximum_reduction
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.spell_policy_targeting import legal_single_spell_targets
from app.combat.spell_save_effect_resolution import compile_spell_save_action
from app.combat.state import build_combatant_state
from app.combat.suppression_zone_cast import cast_suppression_zone, choose_suppression_zone_center
from app.combat.suppression_zone_geometry import verbal_casting_blocked
from app.combat.teleport_resolution import resolve_teleport
from app.combat.timed_self_buff_policy import choose_timed_self_buff_action
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.combat.zero_hp import apply_damage
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.monsters import build_commoner
from app.content.shared_control_spells_2014 import hold_person_2014, silence_2014, spirit_guardians_2014
from app.content.shared_damage_spells_2014 import harm_2014
from app.content.shared_restoration_spells_2014 import greater_restoration_2014, remove_curse_2014
from app.content.shared_teleport_spells_2014 import dimension_door_2014
from app.content.shared_ward_spells_2014 import magic_weapon_2014, protection_from_energy_2014, warding_bond_2014
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.combat.spell_choice import SpellChoice
from app.domain.weapons_base import DamageType


def _member(template, combatant_id: str, side: str, x: int = 0, y: int = 0, slots: dict[int, int] | None = None):
    resources = list(template.resources)
    if slots:
        resources.extend(
            ResourceDefinition(id=f"spell-slot-{level}", name=f"Level {level} Slot", max_uses=count)
            for level, count in slots.items()
        )
    copied = template.model_copy(update={"resources": resources})
    state = build_combatant_state(copied)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _setup(heroes, monsters) -> EncounterSetup:
    return EncounterSetup(
        heroes=heroes,
        monsters=monsters,
        hero_total_levels=max(1, sum(hero.state.template.level or 1 for hero in heroes)),
        monster_total_cr="1/4",
        map_definition=build_standard_iron_pit_map(),
    )


def test_2014_damage_share_fails_closed_without_encounter_setup() -> None:
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 3, 2)
    ally.state.damage_share_source_id = "caster"
    ally.state.damage_share_range_ft = 60
    ally.state.damage_share_effect_id = "warding-bond"
    try:
        apply_damage(ally.state, 4, damage_types={DamageType.SLASHING})
    except ValueError as exc:
        assert "encounter setup" in str(exc)
    else:
        raise AssertionError("Warding Bond share must fail closed when setup is missing.")


def test_2014_warding_bond_shares_post_resistance_damage_and_excludes_self() -> None:
    caster_template = build_karnok_stoneward().model_copy(update={
        "defensive_spell_actions": [warding_bond_2014()],
        "resources": [ResourceDefinition(id="spell-slot-2", name="2nd-level Slot", max_uses=1)],
    })
    caster = _member(caster_template, "caster", "heroes", 2, 2)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 3, 2)
    enemy = _member(build_goblin_warrior(), "enemy", "monsters", 6, 2)
    setup = _setup([caster, ally], [enemy])

    events, _ = prepare_defenses(setup)
    assert events[0].feature_id == "warding-bond"
    assert ally.state.damage_share_source_id == "caster"
    assert caster.state.damage_share_source_id is None
    assert effective_armor_class(ally.state) == ally.state.template.armor_class + 1
    assert saving_throw_flat_bonus(ally.state) == 1

    before_caster = caster.state.current_hp
    before_ally = ally.state.current_hp
    incoming = adjusted_damage_amount(10, DamageType.SLASHING, ally.state)
    assert incoming == 5
    apply_damage(ally.state, incoming, damage_types={DamageType.SLASHING}, setup=setup)
    assert ally.state.current_hp == before_ally - incoming
    assert caster.state.current_hp == before_caster - incoming


def test_2014_hold_person_targets_humanoids_and_paralyzes_on_failed_save() -> None:
    spell = hold_person_2014(13)
    caster = _member(build_karnok_stoneward(), "caster", "heroes", 2, 2)
    humanoid = _member(build_commoner().model_copy(update={"creature_type": "humanoid"}), "humanoid", "monsters", 4, 2)
    beast = _member(build_goblin_warrior().model_copy(update={"creature_type": "beast"}), "beast", "monsters", 5, 2)
    setup = _setup([caster], [humanoid, beast])

    legal = legal_single_spell_targets(caster, setup, spell)
    assert [item.combatant_id for item in legal] == ["humanoid"]

    action = compile_spell_save_action(SpellChoice(spell, 2, (humanoid.combatant_id,)))
    assert legal_save_action(action, humanoid, 10) is True
    assert legal_save_action(action, beast, 10) is False

    event = resolve_save_action(
        1, 1, caster, humanoid, action, 10, FixedDiceProvider([1]), spend_action=False, setup=setup,
    )
    assert event.save_succeeded is False
    assert "paralyzed" in humanoid.state.active_effect_ids
    timed = next(item for item in humanoid.state.timed_effects if item.effect_id == "paralyzed")
    assert timed.repeat_save_ability == "wisdom"
    assert timed.repeat_save_timing == "target_turn_end"


def test_2014_silence_deafens_and_blocks_verbal_spells() -> None:
    caster = _member(build_karnok_stoneward().model_copy(update={
        "suppression_zone_actions": [silence_2014()],
    }), "caster", "heroes", 2, 2, {2: 1})
    enemy = _member(build_commoner(), "enemy", "monsters", 4, 2)
    setup = _setup([caster], [enemy])
    center = choose_suppression_zone_center(caster, setup, silence_2014())
    assert center is not None
    cast_suppression_zone(1, 1, caster, setup, silence_2014(), center, "1:caster")
    assert verbal_casting_blocked(enemy, setup) is True
    assert "deafened" in enemy.state.active_effect_ids
    assert DamageType.THUNDER in enemy.state.zone_damage_immunities


def test_2014_spirit_guardians_deals_half_on_successful_wisdom_save() -> None:
    action = spirit_guardians_2014(13)
    caster = _member(build_karnok_stoneward().model_copy(update={
        "timed_self_buff_actions": [action],
        "resources": [ResourceDefinition(id="spell-slot-3", name="3rd-level Slot", max_uses=1)],
    }), "caster", "heroes", 2, 2)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 40}), "enemy", "monsters", 3, 2)
    setup = _setup([caster], [enemy])
    resolve_timed_self_buff(1, 1, caster, action, setup=setup, turn_key="1:caster")
    before = enemy.state.current_hp
    event, _ = resolve_emanation_hit(
        2, 1, caster, enemy, action, setup, FixedDiceProvider([8, 8, 8, 20]), "1:enemy",
    )
    assert event is not None
    assert event.save_succeeded is True
    assert enemy.state.current_hp == before - 12


def test_2014_spirit_guardians_is_not_chosen_after_a_slot_is_spent() -> None:
    action = spirit_guardians_2014(13)
    caster = _member(build_karnok_stoneward().model_copy(update={
        "timed_self_buff_actions": [action],
        "resources": [ResourceDefinition(id="spell-slot-3", name="3rd-level Slot", max_uses=1)],
    }), "caster", "heroes", 2, 2)
    enemy = _member(build_commoner(), "enemy", "monsters", 3, 2)
    setup = _setup([caster], [enemy])
    assert choose_timed_self_buff_action(caster, setup, turn_key="1:caster") is not None
    caster.state.spell_slot_expended_turn_key = "1:caster"
    assert choose_timed_self_buff_action(caster, setup, turn_key="1:caster") is None
    assert choose_timed_self_buff_action(caster, setup) is not None


def test_2014_protection_from_energy_uses_concentration_owned_resistance() -> None:
    caster = _member(build_karnok_stoneward().model_copy(update={
        "defensive_spell_actions": [protection_from_energy_2014()],
        "resources": [ResourceDefinition(id="spell-slot-3", name="3rd-level Slot", max_uses=1)],
    }), "caster", "heroes", 2, 2)
    enemy = _member(build_goblin_warrior(), "enemy", "monsters", 6, 2)
    setup = _setup([caster], [enemy])
    events, _ = prepare_defenses(setup)
    assert events[0].feature_id == "protection-from-energy"
    assert caster.state.concentration is not None
    assert caster.state.concentration.effect_id == "protection-from-energy"
    owned = [effect for effect in caster.state.timed_effects if effect.source_effect_id == "protection-from-energy"]
    assert owned
    assert owned[0].owned_damage_resistances


def test_2014_remove_curse_ends_every_curse() -> None:
    cleric = _member(build_karnok_stoneward().model_copy(update={
        "condition_removal_actions": [remove_curse_2014()],
        "resources": [ResourceDefinition(id="spell-slot-3", name="3rd-level Slot", max_uses=1)],
    }), "cleric", "heroes", 2, 2)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 3, 2)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 2)
    ally.state.active_curses = ["bestow-curse", "hex"]
    setup = _setup([cleric, ally], [enemy])
    choice = choose_condition_removal_action(cleric, setup, "1:cleric")
    assert choice is not None
    action, target, conditions = choice
    assert conditions == ["curse"]
    resolve_condition_removal(1, 1, cleric, target, action, conditions, "1:cleric")
    assert ally.state.active_curses == []


def test_2014_greater_restoration_applies_exactly_one_selected_rider() -> None:
    cleric = _member(build_karnok_stoneward().model_copy(update={
        "condition_removal_actions": [greater_restoration_2014()],
        "resources": [ResourceDefinition(id="spell-slot-5", name="5th-level Slot", max_uses=1)],
    }), "cleric", "heroes", 2, 2)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 3, 2)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 2)
    ally.state.exhaustion_level = 2
    ally.state.active_curses = ["bestow-curse"]
    ally.state.ability_score_reductions = {"strength": 2}
    apply_hit_point_maximum_reduction(ally, 8)
    setup = _setup([cleric, ally], [enemy])
    choice = choose_condition_removal_action(cleric, setup, "1:cleric")
    assert choice is not None
    action, target, conditions = choice
    assert len(conditions) == 1
    assert conditions[0] in {
        "exhaustion",
        "curse",
        "ability-score-reduction",
        "hit-point-maximum-reduction",
    }
    resolve_condition_removal(1, 1, cleric, target, action, conditions, "1:cleric")
    remaining = 0
    remaining += int(bool(ally.state.exhaustion_level))
    remaining += int(bool(ally.state.active_curses))
    remaining += int(bool(ally.state.ability_score_reductions))
    remaining += int(bool(ally.state.hit_point_maximum_reduction))
    assert remaining == 3


def test_2014_greater_restoration_clears_ability_score_reduction() -> None:
    cleric = _member(build_karnok_stoneward().model_copy(update={
        "condition_removal_actions": [greater_restoration_2014()],
        "resources": [ResourceDefinition(id="spell-slot-5", name="5th-level Slot", max_uses=1)],
    }), "cleric", "heroes", 2, 2)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 3, 2)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 2)
    ally.state.ability_score_reductions = {"constitution": 3, "strength": 2}
    setup = _setup([cleric, ally], [enemy])
    choice = choose_condition_removal_action(cleric, setup, "1:cleric")
    assert choice is not None
    action, target, conditions = choice
    assert conditions == ["ability-score-reduction"]
    resolve_condition_removal(1, 1, cleric, target, action, conditions, "1:cleric")
    assert ally.state.ability_score_reductions == {"strength": 2}


def test_2014_harm_has_no_effect_on_undead() -> None:
    spell = harm_2014(15)
    assert spell.excluded_target_creature_types == ["undead", "construct"]
    caster = _member(build_karnok_stoneward(), "caster", "heroes", 2, 2)
    undead = _member(
        build_commoner().model_copy(update={"creature_type": "undead", "max_hp": 20}),
        "undead",
        "monsters",
        4,
        2,
    )
    setup = _setup([caster], [undead])
    assert legal_single_spell_targets(caster, setup, spell) == []
    action = compile_spell_save_action(SpellChoice(spell, 6, (undead.combatant_id,)))
    assert legal_save_action(action, undead, 10) is False


def test_2014_harm_floors_at_one_hp_and_cuts_maximum_on_a_failed_save() -> None:
    spell = harm_2014(15)
    caster = _member(build_karnok_stoneward(), "caster", "heroes", 2, 2)
    target = _member(build_commoner().model_copy(update={"max_hp": 20}), "target", "monsters", 4, 2)
    target.state.current_hp = 20
    setup = _setup([caster], [target])
    action = compile_spell_save_action(SpellChoice(spell, 6, (target.combatant_id,)))
    resolve_save_action(
        1, 1, caster, target, action, 10, FixedDiceProvider([1] + [6] * 14), spend_action=False, setup=setup,
    )
    assert target.state.current_hp == 1
    assert target.state.hit_point_maximum_reduction == 84
    assert effective_max_hp(target.state) == 1


def test_2014_magic_weapon_adds_plus_one_attack_and_weapon_damage() -> None:
    caster = _member(build_karnok_stoneward().model_copy(update={
        "defensive_spell_actions": [magic_weapon_2014()],
        "resources": [ResourceDefinition(id="spell-slot-2", name="2nd-level Slot", max_uses=1)],
    }), "caster", "heroes", 2, 2)
    enemy = _member(build_goblin_warrior(), "enemy", "monsters", 6, 2)
    setup = _setup([caster], [enemy])
    events, _ = prepare_defenses(setup)
    assert events[0].feature_id == "magic-weapon"
    weapon_id = caster.state.template.weapon_attack.weapon.id
    assert attack_roll_flat_bonus(caster.state, weapon_id) == 1
    assert weapon_damage_flat_bonus(caster.state, weapon_id) == 1


def test_2014_dimension_door_teleports_or_fails_in_occupied_space() -> None:
    caster = _member(build_karnok_stoneward().model_copy(update={
        "teleport_actions": [dimension_door_2014()],
        "resources": [ResourceDefinition(id="spell-slot-4", name="4th-level Slot", max_uses=1)],
        "max_hp": 40,
    }), "caster", "heroes", 1, 2, {4: 1})
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 2)
    setup = _setup([caster], [enemy])
    events, _ = resolve_teleport(
        1, 1, caster, setup, dimension_door_2014(), GridPosition(x=7, y=2),
        FixedDiceProvider([1, 1, 1, 1]), "1:caster",
    )
    assert caster.state.position == GridPosition(x=7, y=2)
    assert events[0].feature_id == "dimension-door"

    blocker = _member(build_commoner(), "blocker", "monsters", 6, 2)
    setup = _setup([caster], [enemy, blocker])
    caster.state.action_available = True
    next(item for item in caster.state.resources if item.id == "spell-slot-4").current_uses = 1
    before = caster.state.current_hp
    failed, _ = resolve_teleport(
        2, 1, caster, setup, dimension_door_2014(), GridPosition(x=6, y=2),
        FixedDiceProvider([6, 6, 6, 6]), "1:caster-b",
    )
    assert caster.state.position == GridPosition(x=7, y=2)
    assert caster.state.current_hp == before - 24
    assert "fails in an occupied space" in failed[0].description
