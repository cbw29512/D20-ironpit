from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_registry
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024


def test_2024_open_hand_monk_level16_applies_wisdom_asi_and_derived_stats() -> None:
    level15 = build_kael_stillwater_2024(15)
    template = build_kael_stillwater_2024(16)
    profile = build_kael_stillwater_2024_profile(16)
    fingerprint = build_kael_2024_combat_profiles(16)[-1]

    assert template.level == profile.level == fingerprint.level == 16
    assert profile.final_ability_scores is not None
    assert level15.ability_scores.wisdom == 12
    assert template.ability_scores.wisdom == 14
    assert fingerprint.abilities.wisdom == 14

    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (17, 131, 55, 10)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (17, 131, 55, 10)
    assert template.saving_throw_bonuses == {
        "strength": 6,
        "dexterity": 10,
        "constitution": 8,
        "intelligence": 5,
        "wisdom": 7,
        "charisma": 5,
    }
    assert template.skill_bonuses["insight"] == 7
    assert template.skill_bonuses["perception"] == 7
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 16

    stunning = template.progression_features.resource_backed_on_hit_save_rider
    assert stunning is not None
    assert stunning.save_dc == 15

    wholeness = template.healing_actions[0]
    assert (wholeness.dice_count, wholeness.dice_size, wholeness.healing_bonus) == (1, 10, 2)

    redirect = template.attack_damage_reduction_reaction.zero_damage_redirect
    assert redirect is not None
    assert redirect.save_dc == 15


def test_2024_open_hand_monk_level16_profile_audit_and_registry_are_certified() -> None:
    profile = build_kael_stillwater_2024_profile(16)
    audits = {item.feature_id: item for item in profile.feature_audits}

    asi = audits["ability-score-improvement-l16"]
    assert asi.combat_relevant is True
    assert asi.automated is True
    assert "Wisdom 12 to 14" in (asi.notes or "")

    registry = build_certified_hero_registry()
    assert registry[("monk", 16, "canonical")] == ("Kael Stillwater", "kael-stillwater-l16")
