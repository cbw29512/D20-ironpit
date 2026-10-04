from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.environment_context import environment_context_disadvantage_sources
from app.combat.resource_conversion import resolve_resource_conversion
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.monsters_humanoid_expansion import build_kobold_warrior
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType, RollMode
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(distance: int = 20) -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    paladin = _member(build_aurelia_brightshield_2024(20), "aurelia", "heroes", 0)
    kobold_template = complete_monster_trait_fingerprints([build_kobold_warrior()])[0]
    kobold = _member(kobold_template, "kobold", "monsters", distance)
    setup = EncounterSetup(
        heroes=[paladin],
        monsters=[kobold],
        hero_total_levels=20,
        monster_total_cr="1/8",
        ruleset="2024",
    )
    return setup, paladin, kobold


def _resource(state, resource_id: str):
    return next(item for item in state.resources if item.id == resource_id)


def _activate(paladin: EncounterCombatant) -> None:
    begin_turn(paladin.state)
    action = next(
        item for item in paladin.state.template.timed_self_buff_actions
        if item.id == "holy-nimbus-2024"
    )
    event = resolve_timed_self_buff(1, 1, paladin, action)
    assert event.feature_id == "holy-nimbus-2024"
    assert _resource(paladin.state, "holy-nimbus").current_uses == 0


def test_level_twenty_composes_holy_nimbus_from_universal_primitives() -> None:
    try:
        previous = build_aurelia_brightshield_2024(19)
        hero = build_aurelia_brightshield_2024(20)
        profile = build_aurelia_brightshield_2024_profile(20)

        assert hero.name == previous.name
        assert hero.level == 20
        assert hero.ability_scores == previous.ability_scores
        assert hero.max_hp == previous.max_hp + 8 == 164
        assert hero.weapon_attack.attack_bonus == 11
        assert hero.skill_bonuses["persuasion"] == 11

        resources = {item.id: item.max_uses for item in hero.resources}
        assert resources["lay-on-hands"] == 100
        assert resources["spell-slot-5"] == 2
        assert resources["boon-combat-prowess"] == 1
        assert resources["holy-nimbus"] == 1

        nimbus = next(item for item in hero.timed_self_buff_actions if item.id == "holy-nimbus-2024")
        assert nimbus.action_cost == "bonus_action"
        assert nimbus.duration_rounds == 100
        assert nimbus.inactive_while_source_incapacitated is True
        assert nimbus.environment_context_aura is not None
        assert nimbus.environment_context_aura.radius_ft == 30
        assert nimbus.environment_context_aura.context_tags == ["sunlight"]
        assert nimbus.start_turn_emanation_damage is not None
        assert (
            nimbus.start_turn_emanation_damage.radius_ft,
            nimbus.start_turn_emanation_damage.fixed_damage,
            nimbus.start_turn_emanation_damage.damage_type,
        ) == (30, 11, DamageType.RADIANT)
        grant = nimbus.saving_throw_advantage_grants[0]
        assert grant.source_creature_types == ["fiend", "undead"]
        assert grant.requires_spell_effect is False
        assert set(grant.abilities) == {
            "strength", "dexterity", "constitution",
            "intelligence", "wisdom", "charisma",
        }

        conversion = next(
            item for item in hero.resource_conversion_actions
            if item.id == "restore-holy-nimbus-2024"
        )
        assert conversion.action_cost == "none"
        assert conversion.source_resource_id == "spell-slot-5"
        assert conversion.source_cost == 1
        assert conversion.target_resource_id == "holy-nimbus"
        assert conversion.target_gain == 1
        assert conversion.requires_target_empty is True

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["holy-nimbus"].combat_relevant is True
        assert audits["holy-nimbus"].automated is True

        fingerprint = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 20)
        assert fingerprint.max_hp == 164
        assert ("lay-on-hands", 100) in fingerprint.resources
        assert ("holy-nimbus", 1) in fingerprint.resources

        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 20 Holy Nimbus certification failed.")
        raise


def test_holy_nimbus_radiant_damage_save_advantage_and_incapacitation_are_live() -> None:
    setup, paladin, kobold = _setup()
    _activate(paladin)

    assert saving_throw_mode(
        paladin.state,
        "wisdom",
        SavingThrowContext(source_creature_type="fiend"),
    ) is RollMode.ADVANTAGE
    assert saving_throw_mode(
        paladin.state,
        "dexterity",
        SavingThrowContext(source_creature_type="undead"),
    ) is RollMode.ADVANTAGE
    assert saving_throw_mode(
        paladin.state,
        "wisdom",
        SavingThrowContext(source_creature_type="fey"),
    ) is RollMode.NORMAL

    before = kobold.state.current_hp
    events, sequence = resolve_target_turn_start_emanations(
        2, 1, kobold, setup, FixedDiceProvider([1]),
    )
    assert sequence == 3
    assert len(events) == 1
    assert events[0].feature_id == "holy-nimbus-2024"
    assert events[0].damage_components[0].total == 11
    assert kobold.state.current_hp == max(0, before - 11)

    paladin.state.is_unconscious = True
    assert saving_throw_mode(
        paladin.state,
        "wisdom",
        SavingThrowContext(source_creature_type="fiend"),
    ) is RollMode.NORMAL
    inactive, inactive_sequence = resolve_target_turn_start_emanations(
        sequence, 2, kobold, setup, FixedDiceProvider([1]),
    )
    assert inactive == []
    assert inactive_sequence == sequence


def test_sunlight_is_context_and_sunlight_sensitivity_is_target_owned() -> None:
    setup, paladin, kobold = _setup()
    reaction = next(
        item for item in kobold.state.template.environment_context_reactions
        if item.context_tag == "sunlight"
    )
    assert reaction.attack_roll_disadvantage is True
    assert reaction.ability_check_disadvantage is True

    assert environment_context_disadvantage_sources(kobold, setup, "attack_roll") == 0
    assert environment_context_disadvantage_sources(kobold, setup, "ability_check") == 0

    _activate(paladin)
    assert environment_context_disadvantage_sources(kobold, setup, "attack_roll") == 1
    assert environment_context_disadvantage_sources(kobold, setup, "ability_check") == 1

    begin_turn(kobold.state)
    event = resolve_encounter_attack(
        2, 1, kobold, paladin, kobold.state.template.weapon_attack, 20,
        FixedDiceProvider([18, 2, 2, 2]),
        setup,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE

    paladin.state.is_unconscious = True
    assert environment_context_disadvantage_sources(kobold, setup, "attack_roll") == 0
    assert environment_context_disadvantage_sources(kobold, setup, "ability_check") == 0


def test_holy_nimbus_use_can_be_restored_by_one_fifth_level_slot_without_action() -> None:
    _, paladin, _ = _setup()
    _activate(paladin)
    slot = _resource(paladin.state, "spell-slot-5")
    before_slots = slot.current_uses
    action = next(
        item for item in paladin.state.template.resource_conversion_actions
        if item.id == "restore-holy-nimbus-2024"
    )

    event = resolve_resource_conversion(
        paladin.state,
        action,
        sequence=2,
        round_number=1,
        actor_id=paladin.combatant_id,
    )

    assert event.feature_id == "restore-holy-nimbus-2024"
    assert slot.current_uses == before_slots - 1
    assert _resource(paladin.state, "holy-nimbus").current_uses == 1
    assert paladin.state.action_available is True
    assert paladin.state.bonus_action_available is False  # spent only by Holy Nimbus activation
