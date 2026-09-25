from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package, prepared_count_2014
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType, RollMode
from app.domain.saving_throw_context import SavingThrowContext


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(target_position: int = 25, *, radiant_resistance: bool = False):
    paladin = _member(build_aurelia_brightshield_2014(20), "aurelia", "heroes", 0)
    target_template = build_kael_stillwater_2014(1)
    if radiant_resistance:
        target_template = target_template.model_copy(update={"damage_resistances": [DamageType.RADIANT]})
    target = _member(target_template, "target", "monsters", target_position)
    setup = EncounterSetup(
        heroes=[paladin], monsters=[target], hero_total_levels=20, monster_total_cr="1", ruleset="2014",
    )
    return setup, paladin, target


def _activate(paladin: EncounterCombatant) -> None:
    begin_turn(paladin.state)
    action = paladin.state.template.timed_self_buff_actions[0]
    event = resolve_timed_self_buff(1, 1, paladin, action)
    assert event.feature_id == "holy-nimbus"
    assert next(item for item in paladin.state.resources if item.id == "holy-nimbus").current_uses == 0


def test_level_20_is_incremental_holy_nimbus_progression() -> None:
    level19 = build_aurelia_brightshield_2014(19)
    hero = build_aurelia_brightshield_2014(20)
    profile = build_aurelia_brightshield_2014_profile(20)
    combat = build_aurelia_brightshield_2014_combat_profile(20)

    assert hero.level == 20
    assert hero.max_hp == level19.max_hp + 8 == 164
    assert hero.ability_scores == level19.ability_scores
    assert hero.progression_features.aura_radius_2014_ft == 30
    assert hero.progression_features.aura_of_protection_2014_bonus == 5
    assert len(hero.timed_self_buff_actions) == 1

    nimbus = hero.timed_self_buff_actions[0]
    assert (nimbus.id, nimbus.resource_id, nimbus.resource_cost, nimbus.duration_rounds) == (
        "holy-nimbus", "holy-nimbus", 1, 10,
    )
    assert nimbus.start_turn_emanation_damage is not None
    assert (
        nimbus.start_turn_emanation_damage.radius_ft,
        nimbus.start_turn_emanation_damage.fixed_damage,
        nimbus.start_turn_emanation_damage.damage_type,
    ) == (30, 10, DamageType.RADIANT)
    grant = nimbus.saving_throw_advantage_grants[0]
    assert grant.requires_spell_effect is True
    assert grant.source_creature_types == ["fiend", "undead"]
    assert set(grant.abilities) == {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    }

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["lay-on-hands"] == 100
    assert resources["cleansing-touch"] == 5
    assert resources["holy-nimbus"] == 1
    assert [resources[f"spell-slot-{level}"] for level in range(1, 6)] == [4, 3, 3, 3, 2]

    charisma_modifier = hero.ability_scores.modifier("charisma")
    assert prepared_count_2014(20, charisma_modifier) == 15
    package = build_paladin_2014_spell_package(20, charisma_modifier)
    assert package is not None and len(package.spells) == 15
    magic_circle = next(spell for spell in package.spells if spell.id == "magic-circle")
    assert magic_circle.spell_level == 3
    assert magic_circle.required_capabilities == ["arena-out-of-scope"]

    audit = next(item for item in profile.feature_audits if item.feature_id == "holy-nimbus")
    assert audit.automated is True
    assert_character_resources_raw_ready(hero, profile, combat)


def test_holy_nimbus_save_advantage_is_timed_and_requires_fiend_or_undead_spell_source() -> None:
    setup, paladin, _ = _setup()
    _activate(paladin)

    fiend_spell = SavingThrowContext(spell_effect=True, source_creature_type="fiend")
    undead_spell = SavingThrowContext(spell_effect=True, source_creature_type="undead")
    fiend_nonspell = SavingThrowContext(spell_effect=False, source_creature_type="fiend")
    fey_spell = SavingThrowContext(spell_effect=True, source_creature_type="fey")

    assert saving_throw_mode(paladin.state, "wisdom", fiend_spell) is RollMode.ADVANTAGE
    assert saving_throw_mode(paladin.state, "dexterity", undead_spell) is RollMode.ADVANTAGE
    assert saving_throw_mode(paladin.state, "wisdom", fiend_nonspell) is RollMode.NORMAL
    assert saving_throw_mode(paladin.state, "wisdom", fey_spell) is RollMode.NORMAL

    events, _ = expire_start_of_turn_conditions(2, 11, paladin, setup)
    assert any(event.feature_id == "holy-nimbus" for event in events)
    assert saving_throw_mode(paladin.state, "wisdom", fiend_spell) is RollMode.NORMAL


def test_holy_nimbus_enemy_turn_start_emanation_uses_range_and_radiant_defenses() -> None:
    setup, paladin, target = _setup(radiant_resistance=True)
    _activate(paladin)
    before = target.state.current_hp

    events, sequence = resolve_target_turn_start_emanations(
        2, 1, target, setup, FixedDiceProvider([1]),
    )

    assert sequence == 3
    assert len(events) == 1
    event = events[0]
    assert event.feature_id == "holy-nimbus"
    assert event.distance_before_ft == 25
    assert event.damage_components[0].total == 10
    assert event.damage_components[0].applied_total == 5
    assert target.state.current_hp == before - 5

    target.position_ft = 35
    later, later_sequence = resolve_target_turn_start_emanations(
        sequence, 2, target, setup, FixedDiceProvider([1]),
    )
    assert later == []
    assert later_sequence == sequence
