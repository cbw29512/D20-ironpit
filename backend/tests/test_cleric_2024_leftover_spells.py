from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.defensive_spell_resolution import resolve_defensive_spell
from app.combat.dice import FixedDiceProvider
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.group_healing import choose_group_healing_targets, resolve_group_healing
from app.combat.healing_policy import choose_healing_action
from app.combat.healing import resolve_healing
from app.combat.spell_choice import SpellChoice
from app.combat.spell_save_effect_resolution import resolve_spell_save_effect
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.combat.zero_hp import apply_damage
from app.combat.zero_hp_replacement import (
    consume_instant_death_prevention,
    consume_zero_hp_replacement_log,
)
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_fighter import build_karnok_stoneward
from app.content.canonical_hero_policy import canonical_spell_package
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.modifiers import ModifierKind


def _member(template, combatant_id: str, side: str, x: int = 4, y: int = 7) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=abs(x) * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _setup(heroes, monsters) -> EncounterSetup:
    return EncounterSetup(
        heroes=heroes,
        monsters=monsters,
        hero_total_levels=sum((item.state.template.level or 1) for item in heroes),
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )


def _slot(member: EncounterCombatant, level: int):
    return next(item for item in member.state.resources if item.id == f"spell-slot-{level}")


def test_death_ward_2024_replaces_zero_hp_and_blocks_instant_kill() -> None:
    cleric = _member(build_seraphine_dawnshield_level(7), "cleric", "heroes")
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5, 7)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 7)
    setup = _setup([cleric, ally], [enemy])
    ward = next(item for item in cleric.state.template.defensive_spell_actions if item.id == "death-ward")
    resolve_defensive_spell(
        1, cleric, [ally], ward, 4, _slot(cleric, 4),
        [item.state for item in [*setup.heroes, *setup.monsters]],
    )
    ally.state.current_hp = 5
    assert apply_damage(ally.state, 20) == "zero_hp_replacement"
    assert ally.state.current_hp == 1
    assert "Death Ward prevents the drop to 0 HP" in consume_zero_hp_replacement_log(ally.state)

    cleric2 = _member(build_seraphine_dawnshield_level(7), "cleric2", "heroes")
    ally2 = _member(build_karnok_stoneward(), "ally2", "heroes", 5, 7)
    resolve_defensive_spell(
        1, cleric2, [ally2], ward, 4, _slot(cleric2, 4), [cleric2.state, ally2.state],
    )
    assert consume_instant_death_prevention(ally2.state) is True
    assert "Death Ward negates an instant-death effect" in consume_zero_hp_replacement_log(ally2.state)


def test_heal_and_spare_the_dying_follow_healing_policy() -> None:
    cleric = _member(build_seraphine_dawnshield_level(11), "cleric", "heroes")
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5, 7)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 7)
    setup = _setup([cleric, ally], [enemy])
    heal = next(item for item in cleric.state.template.healing_actions if item.id == "heal")
    assert heal.healing_bonus == 78
    assert heal.removable_conditions == ["blinded", "deafened", "poisoned"]
    spare = next(item for item in cleric.state.template.healing_actions if item.id == "spare-the-dying")
    assert spare.stabilize_at_zero is True
    assert spare.range_ft == 60

    ally.state.current_hp = 0
    ally.state.is_unconscious = True
    choice = choose_healing_action(cleric, setup, "1:cleric")
    assert choice is not None
    assert choice[0].id == "healing-word"

    for resource in cleric.state.resources:
        if resource.id.startswith("spell-slot-"):
            resource.current_uses = 0
    begin_turn(cleric.state)
    choice = choose_healing_action(cleric, setup, "1:cleric")
    assert choice is not None and choice[0].id == "spare-the-dying"
    event = resolve_healing(1, 1, cleric, ally, spare, FixedDiceProvider([]), "1:cleric")
    assert ally.state.is_stable is True
    assert ally.state.current_hp == 0
    assert event.healing_roll is not None
    assert event.healing_roll.notation == "stabilize"


def test_mass_heal_divides_the_printed_pool() -> None:
    cleric = _member(build_seraphine_dawnshield_level(17), "cleric", "heroes")
    first = _member(build_karnok_stoneward(), "first", "heroes", 5, 7)
    second = _member(build_karnok_stoneward(), "second", "heroes", 5, 8)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 7)
    setup = _setup([cleric, first, second], [enemy])
    action = next(item for item in cleric.state.template.healing_actions if item.id == "mass-heal")
    assert action.shared_healing_pool == 700
    assert action.healing_bonus == 11
    first.state.current_hp = 0
    second.state.current_hp = 2
    targets = choose_group_healing_targets(cleric, setup, action, "1:cleric")
    assert [item.combatant_id for item in targets][:2] == ["first", "second"]
    events, _ = resolve_group_healing(
        1, 1, cleric, targets, action, FixedDiceProvider([]), "1:cleric", setup=setup,
    )
    assert first.state.current_hp == first.state.template.max_hp
    assert second.state.current_hp == second.state.template.max_hp
    assert events[0].healing_roll is not None
    assert events[0].healing_roll.total == first.state.template.max_hp + 11


def test_holy_aura_grants_all_save_advantage_and_is_not_auto_cast() -> None:
    cleric = _member(build_seraphine_dawnshield_level(15), "cleric", "heroes")
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5, 7)
    enemy = _member(build_commoner(), "enemy", "monsters", 8, 7)
    setup = _setup([cleric, ally], [enemy])
    aura = next(item for item in cleric.state.template.timed_self_buff_actions if item.id == "holy-aura")
    assert aura.friendly_save_advantage_aura is not None
    assert aura.friendly_save_advantage_aura.all_saves is True
    from app.combat.timed_self_buff_policy import choose_timed_self_buff_action
    begin_turn(cleric.state)
    assert choose_timed_self_buff_action(cleric, setup) is None or choose_timed_self_buff_action(cleric, setup).id != "holy-aura"
    resolve_timed_self_buff(1, 1, cleric, aura, setup=setup, turn_key="1:cleric")
    sync_friendly_save_auras(setup)
    kinds = {item.kind for item in ally.state.active_modifiers}
    assert ModifierKind.SAVING_THROW_ADVANTAGE in kinds
    assert ModifierKind.ATTACKS_AGAINST_DISADVANTAGE in kinds
    assert any(
        item.kind is ModifierKind.SAVING_THROW_ADVANTAGE and not item.required_effect_tags
        for item in ally.state.active_modifiers
    )


def test_contagion_is_fail_only_poison_and_con_save_disadvantage() -> None:
    cleric = _member(build_seraphine_dawnshield_level(10), "cleric", "heroes")
    enemy = _member(build_commoner().model_copy(update={"max_hp": 80}, deep=True), "enemy", "monsters", 5, 7)
    setup = _setup([cleric], [enemy])
    spell = next(item for item in cleric.state.template.spell_save_actions if item.id == "contagion")
    assert (spell.damage_dice_count, spell.damage_dice_size, spell.success_damage) == (11, 8, "none")
    begin_turn(cleric.state)
    fail_dice = FixedDiceProvider([1, *[8] * 11])
    events, _ = resolve_spell_save_effect(
        1, 1, cleric, setup,
        SpellChoice(action=spell, slot_level=5, target_ids=("enemy",)),
        "1:cleric",
        fail_dice,
    )
    assert events[0].save_succeeded is False
    assert "poisoned" in enemy.state.active_effect_ids
    assert any(
        item.kind is ModifierKind.SAVING_THROW_DISADVANTAGE and item.save_ability == "constitution"
        for item in enemy.state.active_modifiers
    )
    poison = next(item for item in enemy.state.timed_effects if item.effect_id == "poisoned")
    assert poison.repeat_save_failures_to_lock == 3

    success_cleric = _member(build_seraphine_dawnshield_level(10), "cleric2", "heroes")
    success_enemy = _member(build_commoner().model_copy(update={"max_hp": 80}, deep=True), "enemy2", "monsters", 5, 7)
    success_setup = _setup([success_cleric], [success_enemy])
    begin_turn(success_cleric.state)
    ok_events, _ = resolve_spell_save_effect(
        1, 1, success_cleric, success_setup,
        SpellChoice(action=spell, slot_level=5, target_ids=("enemy2",)),
        "1:cleric2",
        FixedDiceProvider([20]),
    )
    assert ok_events[0].save_succeeded is True
    assert success_enemy.state.current_hp == 80
    assert "poisoned" not in success_enemy.state.active_effect_ids


def test_contagion_repeat_save_success_ends_and_failures_count() -> None:
    cleric = _member(build_seraphine_dawnshield_level(10), "cleric", "heroes")
    enemy = _member(build_commoner().model_copy(update={"max_hp": 80}, deep=True), "enemy", "monsters", 5, 7)
    setup = _setup([cleric], [enemy])
    spell = next(item for item in cleric.state.template.spell_save_actions if item.id == "contagion")
    begin_turn(cleric.state)
    resolve_spell_save_effect(
        1, 1, cleric, setup,
        SpellChoice(action=spell, slot_level=5, target_ids=("enemy",)),
        "1:cleric",
        FixedDiceProvider([1, *[8] * 11]),
    )
    resolve_target_condition_timing(2, 2, enemy, "target_turn_end", FixedDiceProvider([1]))
    poison = next(item for item in enemy.state.timed_effects if item.effect_id == "poisoned")
    assert poison.repeat_save_failure_count == 1
    resolve_target_condition_timing(3, 3, enemy, "target_turn_end", FixedDiceProvider([20]))
    assert "poisoned" not in enemy.state.active_effect_ids
    assert not any(item.source_effect_id == "contagion" for item in enemy.state.active_modifiers)


def test_prayer_of_healing_and_regenerate_stay_long_cast_on_the_sheet() -> None:
    seven = canonical_spell_package("cleric", 7)
    thirteen = canonical_spell_package("cleric", 13)
    prayer = next(item for item in seven.spells if item.id == "prayer-of-healing")
    regenerate = next(item for item in thirteen.spells if item.id == "regenerate")
    assert prayer.required_capabilities == ["long-cast"]
    assert regenerate.required_capabilities == ["long-cast"]
    hero = build_seraphine_dawnshield_level(13)
    assert all(item.id != "prayer-of-healing" for item in hero.healing_actions)
    assert all(item.id != "regenerate" for item in hero.healing_actions)


def test_zone_of_truth_and_commune_stay_noncombat_on_the_paladin_sheet() -> None:
    from app.content.canonical_paladin_spells import PALADIN_SPELLS

    by_id = {item.id: item for item in PALADIN_SPELLS}
    assert by_id["zone-of-truth"].required_capabilities == ["arena-out-of-scope"]
    assert by_id["commune"].required_capabilities == ["arena-out-of-scope"]
