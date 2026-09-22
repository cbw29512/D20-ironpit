from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, mara_rogue_features, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level19_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level19_profile


def test_2024_rogue_level19_applies_night_spirit_asi_and_sneak_attack_scaling() -> None:
    level18 = build_mara_quickstep_level(18)
    template = build_mara_quickstep_level(19)

    assert unsupported_mara_rogue_features(19) == ()
    assert "rogue-epic-boon" in mara_rogue_features(19)
    assert template.level == 19
    assert template.ability_scores is not None
    assert template.ability_scores.strength == 14
    assert template.max_hp == 193
    assert template.max_hp - level18.max_hp == 10
    assert template.skill_bonuses["athletics"] == 8
    assert template.progression_features.sneak_attack_d6 == 10


def test_2024_rogue_level19_night_spirit_shadow_riders_are_explicitly_arena_inert() -> None:
    profile = build_mara_quickstep_level19_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    boon = audits["rogue-epic-boon"]

    assert profile.level == 19
    assert profile.final_ability_scores.strength == 14
    assert profile.ability_score_maximums["strength"] == 30
    assert boon.name == "Boon of the Night Spirit"
    assert boon.combat_relevant is False
    assert boon.automated is False
    assert "Dim Light or Darkness" in (boon.notes or "")
    assert "arena-inert" in (boon.notes or "")


def test_2024_rogue_level19_fingerprint_and_registry_match() -> None:
    fingerprint = build_mara_quickstep_level19_combat_profile()
    assert fingerprint.abilities.strength == 14
    assert ("athletics", 8) in fingerprint.skill_bonuses
    assert fingerprint.max_hp == 193
    assert fingerprint.sneak_attack_d6 == 10

    registry = build_certified_hero_registry()
    assert registry[("rogue", 19, "canonical")] == ("Mara Quickstep", "mara-quickstep-l19")
