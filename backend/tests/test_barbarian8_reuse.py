from __future__ import annotations

from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level8_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def test_2024_barbarian_level8_reuses_existing_engine_with_strength_asi() -> None:
    try:
        profile = build_rokhan_stonefury_level8_profile()
        template = build_rokhan_stonefury_level(8)

        assert profile.level == 8
        assert profile.final_ability_scores.strength == 20
        assert profile.final_ability_scores.constitution == 16
        assert template.level == 8
        assert template.max_hp == 85
        assert template.weapon_attack.attack_bonus == 8
        assert template.weapon_attack.damage_bonus == 5
        assert template.saving_throw_bonuses["strength"] == 8
        assert template.skill_bonuses["athletics"] == 8
        assert template.progression_features.frenzy is True
        assert template.progression_features.reckless_attack is True
        assert template.progression_features.danger_sense is True
        assert template.progression_features.mindless_rage is True
        assert template.progression_features.initiative_advantage is True
        assert template.progression_features.instinctive_pounce_fraction == 0.5
        assert ("barbarian", 8, "canonical") in build_certified_hero_registry()

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["ability-score-improvement-l8"].automated is True
    except Exception as exc:
        raise AssertionError("2024 Barbarian level 8 reuse/certification regression failed.") from exc
