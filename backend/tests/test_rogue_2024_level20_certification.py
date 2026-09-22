from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level20_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level20_profile


def test_2024_rogue_level20_uses_universal_failed_d20_replacement() -> None:
    template = build_mara_quickstep_level(20)
    profile = build_mara_quickstep_level20_profile()
    stroke = next(item for item in profile.feature_audits if item.feature_id == "stroke-of-luck")

    assert unsupported_mara_rogue_features(20) == ()
    assert template.level == 20
    assert template.max_hp == 203
    assert template.progression_features.sneak_attack_d6 == 10
    grants = template.progression_features.failed_d20_test_override_grants
    assert len(grants) == 1
    assert grants[0].source_id == "stroke-of-luck"
    assert grants[0].source_name == "Stroke of Luck"
    assert grants[0].resource_id == "stroke-of-luck"
    assert grants[0].replacement_roll == 20
    assert grants[0].test_kinds == ["attack", "saving_throw", "ability_check"]
    assert template.progression_features.miss_to_hit_override_resource_id is None
    assert stroke.combat_relevant is True
    assert stroke.automated is True


def test_2024_stroke_of_luck_turns_failed_attack_into_natural_twenty_critical() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(20))
    defender = build_combatant_state(build_karnok_stoneward_level(18))

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([1, *([4] * 40)]), spend_action=False,
    )

    assert event.attack_roll is not None
    assert event.attack_roll.selected_roll == 20
    assert event.hit is True
    assert event.critical is True
    assert event.turn_terminated is False
    assert event.feature_id == "stroke-of-luck"
    assert "Stroke of Luck turns the failed attack roll into a 20." in event.description
    assert next(item for item in attacker.resources if item.id == "stroke-of-luck").current_uses == 0


def test_2024_rogue_level20_profile_fingerprint_and_registry_match() -> None:
    fingerprint = build_mara_quickstep_level20_combat_profile()
    assert fingerprint.level == 20
    assert fingerprint.max_hp == 203
    assert fingerprint.sneak_attack_d6 == 10
    assert ("stroke-of-luck", 1) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 20, "canonical")] == ("Mara Quickstep", "mara-quickstep-l20")
