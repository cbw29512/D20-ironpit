from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_registry
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024


def test_2024_open_hand_monk_level8_applies_split_asi_and_derived_stats() -> None:
    template = build_kael_stillwater_2024(8)
    profile = build_kael_stillwater_2024_profile(8)
    fingerprint = build_kael_2024_combat_profiles(8)[-1]

    assert template.level == profile.level == fingerprint.level == 8
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 16)
    assert profile.final_ability_scores == template.ability_scores == fingerprint.abilities
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (15, 67, 45, 8)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (15, 67, 45, 8)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (8, 5)
    assert template.saving_throw_bonuses["dexterity"] == 8
    assert template.skill_bonuses["acrobatics"] == 8
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 8


def test_2024_open_hand_monk_level8_profile_and_registry_are_certified() -> None:
    profile = build_kael_stillwater_2024_profile(8)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["ability-score-improvement-l8"].automated is True
    assert "Dexterity 19 to 20" in (audits["ability-score-improvement-l8"].notes or "")
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("dexterity", 2),
        ("dexterity", 1),
        ("constitution", 1),
    ]

    registry = build_certified_hero_registry()
    assert registry[("monk", 8, "canonical")] == ("Kael Stillwater", "kael-stillwater-l8")
