from __future__ import annotations

from app.content.barbarian_berserker_mid_profile import build_rokhan_stonefury_level11_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def test_2024_barbarian_level11_reuses_effect_bound_survival_save() -> None:
    profile = build_rokhan_stonefury_level11_profile()
    template = build_rokhan_stonefury_level(11)
    rule = template.progression_features.effect_bound_survival_save
    assert profile.level == 11
    assert template.max_hp == 115
    assert rule is not None
    assert rule.source_id == "relentless-rage"
    assert rule.required_effect_id == "rage"
    assert rule.save_ability == "constitution"
    assert rule.initial_dc == 10
    assert rule.dc_increment == 5
    assert rule.replacement_hp == 22
    assert ("barbarian", 11, "canonical") in build_certified_hero_registry()
    assert {item.feature_id: item for item in profile.feature_audits}["relentless-rage"].automated is True
