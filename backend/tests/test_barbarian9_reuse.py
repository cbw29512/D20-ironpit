from __future__ import annotations

from app.content.barbarian_berserker_high_profile import build_rokhan_stonefury_level9_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def test_2024_barbarian_level9_reuses_universal_brutal_strike() -> None:
    try:
        profile = build_rokhan_stonefury_level9_profile()
        template = build_rokhan_stonefury_level(9)

        assert profile.level == 9
        assert profile.final_ability_scores.strength == 20
        assert template.level == 9
        assert template.max_hp == 95
        assert template.rage_damage_bonus == 3
        assert template.progression_features.brutal_strike_damage_dice == 1
        assert template.progression_features.reckless_attack is True
        assert template.progression_features.frenzy is True
        assert ("barbarian", 9, "canonical") in build_certified_hero_registry()

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["brutal-strike"].automated is True
    except Exception as exc:
        raise AssertionError("2024 Barbarian level 9 reuse/certification regression failed.") from exc
