from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_registry
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024


def test_2024_open_hand_monk_level12_applies_wisdom_asi_and_derived_stats() -> None:
    template = build_kael_stillwater_2024(12)
    profile = build_kael_stillwater_2024_profile(12)
    fingerprint = build_kael_2024_combat_profiles(12)[-1]

    assert template.level == profile.level == fingerprint.level == 12
    assert template.ability_scores is not None
    assert template.ability_scores.wisdom == 12
    assert profile.final_ability_scores == template.ability_scores == fingerprint.abilities
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (16, 99, 50, 9)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (16, 99, 50, 9)
    assert template.weapon_attack.attack_bonus == 9
    assert template.weapon_attack.damage_bonus == 5
    assert template.skill_bonuses["insight"] == 5
    assert template.skill_bonuses["perception"] == 5
    assert dict(fingerprint.skill_bonuses)["insight"] == 5
    assert dict(fingerprint.skill_bonuses)["perception"] == 5
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 12


def test_2024_open_hand_monk_level12_updates_wisdom_based_features() -> None:
    template = build_kael_stillwater_2024(12)
    profile = build_kael_stillwater_2024_profile(12)
    audits = {item.feature_id: item for item in profile.feature_audits}

    stunning = template.progression_features.resource_backed_on_hit_save_rider
    assert stunning is not None
    assert stunning.save_dc == 13

    wholeness = next(item for item in template.healing_actions if item.id == "wholeness-of-body")
    assert wholeness.dice_size == 10
    assert wholeness.healing_bonus == 1

    assert audits["ability-score-improvement-l12"].automated is True
    assert "+2 Wisdom" in audits["ability-score-improvement-l12"].feature_name

    registry = build_certified_hero_registry()
    assert registry[("monk", 12, "canonical")] == ("Kael Stillwater", "kael-stillwater-l12")
