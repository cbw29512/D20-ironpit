from __future__ import annotations

from app.content.audited_rogue import (
    build_mara_quickstep_level,
    mara_rogue_features,
    unsupported_mara_rogue_features,
)
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level13_combat_profile
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level13_profile


def test_2024_rogue_level13_is_level12_plus_pb_sneak_and_use_magic_device_audit() -> None:
    level12 = build_mara_quickstep_level(12)
    template = build_mara_quickstep_level(13)

    assert "thief-use-magic-device" in mara_rogue_features(13)
    assert unsupported_mara_rogue_features(13) == ()
    assert template.id == "mara-quickstep-l13"
    assert template.level == 13
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 20)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 133, 5)
    assert template.max_hp - level12.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (10, 5)
    assert template.saving_throw_bonuses["dexterity"] == 10
    assert template.saving_throw_bonuses["constitution"] == 5
    assert template.skill_bonuses == {"athletics": 6, "acrobatics": 10}
    assert template.progression_features.sneak_attack_d6 == 7
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.cunning_strike_max_effects == 2
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 5
    assert "Rogue 13" in template.source


def test_2024_rogue_level13_preserves_use_magic_device_without_fake_items() -> None:
    profile = build_mara_quickstep_level13_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    feature = audits["thief-use-magic-device"]

    assert profile.level == 13
    assert feature.combat_relevant is False
    assert feature.automated is False
    assert "no qualifying attunement overflow" in (feature.notes or "")
    assert "treasure integration can activate it later" in (feature.notes or "")


def test_2024_rogue_level13_fingerprint_and_registry_match_runtime() -> None:
    fingerprint = build_mara_quickstep_level13_combat_profile()
    assert (fingerprint.abilities.dexterity, fingerprint.abilities.constitution) == (20, 20)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 133, 7)
    assert ("adrenaline-rush", 5) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 13, "canonical")] == ("Mara Quickstep", "mara-quickstep-l13")
