from __future__ import annotations

from app.content.barbarian_berserker_endgame_profile import build_rokhan_stonefury_level13_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def test_2024_barbarian_level13_binds_improved_brutal_strike_to_universal_sundering() -> None:
    profile = build_rokhan_stonefury_level13_profile()
    template = build_rokhan_stonefury_level(13)

    assert profile.level == 13
    assert template.level == 13
    assert template.max_hp == 148
    assert template.progression_features.brutal_strike_damage_dice == 1
    assert template.progression_features.brutal_strike_sundering is True
    assert ("barbarian", 13, "canonical") in build_certified_hero_registry()

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["improved-brutal-strike"].automated is True
