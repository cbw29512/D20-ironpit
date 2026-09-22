from __future__ import annotations

from app.combat.modifier_stack import (
    expire_source_turn_modifiers,
    next_attack_against_advantage_sources,
)
from app.combat.state import begin_turn, build_combatant_state
from app.combat.stationary_attack_advantage import use_stationary_attack_advantage
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.rogue_progression_profile import build_mara_quickstep_level3_profile
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level3_combat_profile
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_2024_rogue_level3_has_researched_thief_and_steady_aim_progression() -> None:
    template = build_mara_quickstep_level(3)
    assert unsupported_mara_rogue_features(3) == ()
    assert template.id == "mara-quickstep-l3"
    assert template.level == 3
    assert template.max_hp == 24
    assert template.progression_features.sneak_attack_d6 == 2
    assert template.progression_features.cunning_action is True
    assert template.progression_features.stationary_bonus_action_next_attack_advantage is True


def test_2024_rogue_level3_profile_audits_thief_utility_features_without_fake_combat() -> None:
    profile = build_mara_quickstep_level3_profile()
    assert profile.template_id == "mara-quickstep-l3"
    assert profile.level == 3
    assert (profile.subclass_id, profile.subclass_name) == ("thief", "Thief")

    audits = {feature.feature_id: feature for feature in profile.feature_audits}
    assert audits["steady-aim"].combat_relevant is True
    assert audits["steady-aim"].automated is True
    assert audits["thief-fast-hands"].combat_relevant is False
    assert audits["thief-fast-hands"].automated is False
    assert "no qualifying combat item" in (audits["thief-fast-hands"].notes or "")
    assert audits["thief-second-story-work"].combat_relevant is False


def test_stationary_attack_advantage_spends_bonus_action_and_all_movement() -> None:
    rogue = _member(build_mara_quickstep_level(3), "mara", "heroes", 0)
    target = _member(build_karnok_stoneward_level(3), "target", "monsters", 5)
    setup = EncounterSetup(
        heroes=[rogue], monsters=[target], hero_total_levels=3, monster_total_cr="3", ruleset="2024",
    )
    begin_turn(rogue.state)

    event = use_stationary_attack_advantage(1, 1, rogue, setup, feature_id="steady-aim")
    assert event is not None and event.feature_id == "steady-aim"
    assert rogue.state.bonus_action_available is False
    assert rogue.state.movement_remaining_ft == 0
    assert next_attack_against_advantage_sources(rogue.state, target.combatant_id) == 1

    assert expire_source_turn_modifiers([rogue.state], rogue.combatant_id, 1) == 1
    assert next_attack_against_advantage_sources(rogue.state, target.combatant_id) == 0


def test_stationary_attack_advantage_declines_after_movement_or_without_feature() -> None:
    rogue = _member(build_mara_quickstep_level(3), "mara", "heroes", 0)
    target = _member(build_karnok_stoneward_level(3), "target", "monsters", 5)
    setup = EncounterSetup(
        heroes=[rogue], monsters=[target], hero_total_levels=3, monster_total_cr="3", ruleset="2024",
    )
    begin_turn(rogue.state)
    rogue.state.movement_remaining_ft -= 5
    assert use_stationary_attack_advantage(1, 1, rogue, setup, feature_id="steady-aim") is None
    assert rogue.state.bonus_action_available is True

    level2 = _member(build_mara_quickstep_level(2), "mara-l2", "heroes", 0)
    begin_turn(level2.state)
    setup.heroes = [level2]
    assert use_stationary_attack_advantage(1, 1, level2, setup, feature_id="steady-aim") is None


def test_2024_rogue_level3_fingerprint_and_certification_registry_match() -> None:
    fingerprint = build_mara_quickstep_level3_combat_profile()
    assert fingerprint.template_id == "mara-quickstep-l3"
    assert fingerprint.max_hp == 24
    assert fingerprint.sneak_attack_d6 == 2

    registry = build_certified_hero_registry()
    assert registry[("rogue", 3, "canonical")] == ("Mara Quickstep", "mara-quickstep-l3")
