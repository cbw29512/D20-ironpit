from __future__ import annotations

from app.content.barbarian_berserker_endgame_profile import build_rokhan_stonefury_level12_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def test_2024_barbarian_level12_reuses_shared_asi_math() -> None:
    try:
        profile = build_rokhan_stonefury_level12_profile()
        template = build_rokhan_stonefury_level(12)

        assert profile.level == 12
        assert profile.final_ability_scores.constitution == 18
        assert template.level == 12
        assert template.max_hp == 137
        assert template.armor_class == 15
        assert template.saving_throw_bonuses["constitution"] == 8
        assert ("barbarian", 12, "canonical") in build_certified_hero_registry()

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["ability-score-improvement-l12"].automated is True
    except Exception as exc:
        raise AssertionError("2024 Barbarian level 12 ASI reuse/certification regression failed.") from exc
