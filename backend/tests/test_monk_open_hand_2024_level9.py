from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_registry
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024


def test_2024_open_hand_monk_level9_advances_proficiency_focus_and_derived_stats() -> None:
    template = build_kael_stillwater_2024(9)
    profile = build_kael_stillwater_2024_profile(9)
    fingerprint = build_kael_2024_combat_profiles(9)[-1]

    assert template.level == profile.level == fingerprint.level == 9
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 16)
    assert profile.final_ability_scores == template.ability_scores == fingerprint.abilities
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (15, 75, 45, 9)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (15, 75, 45, 9)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (9, 5)
    assert template.saving_throw_bonuses["dexterity"] == 9
    assert template.skill_bonuses["acrobatics"] == 9
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 9


def test_2024_open_hand_monk_level9_audits_acrobatic_movement_as_arena_neutral() -> None:
    profile = build_kael_stillwater_2024_profile(9)
    audits = {item.feature_id: item for item in profile.feature_audits}

    acrobatic = audits["acrobatic-movement"]
    assert acrobatic.combat_relevant is False
    assert acrobatic.automated is False
    assert "vertical surfaces" in (acrobatic.notes or "")
    assert "liquid-terrain state" in (acrobatic.notes or "")

    registry = build_certified_hero_registry()
    assert registry[("monk", 9, "canonical")] == ("Kael Stillwater", "kael-stillwater-l9")
