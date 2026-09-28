from __future__ import annotations

from app.content.barbarian_berserker_high_profile import build_rokhan_stonefury_level10_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def test_2024_barbarian_level10_reuses_universal_damage_reaction() -> None:
    try:
        profile = build_rokhan_stonefury_level10_profile()
        template = build_rokhan_stonefury_level(10)

        assert profile.level == 10
        assert template.level == 10
        assert template.max_hp == 105
        assert template.damage_reaction_attack is not None
        assert template.damage_reaction_attack.source_feature == "retaliation"
        assert template.damage_reaction_attack.attack_kind == "melee"
        assert template.damage_reaction_attack.trigger == "damaged-by-creature"
        assert ("barbarian", 10, "canonical") in build_certified_hero_registry()

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["retaliation"].automated is True
    except Exception as exc:
        raise AssertionError("2024 Barbarian level 10 Retaliation reuse/certification regression failed.") from exc
