from __future__ import annotations

from app.content.barbarian_berserker_endgame_profile import (
    build_rokhan_stonefury_level10_profile,
    build_rokhan_stonefury_level11_profile,
    build_rokhan_stonefury_level12_profile,
)
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def test_2024_barbarian_levels10_to12_reuse_universal_engine() -> None:
    level10 = build_rokhan_stonefury_level(10)
    level11 = build_rokhan_stonefury_level(11)
    level12 = build_rokhan_stonefury_level(12)

    assert build_rokhan_stonefury_level10_profile().level == 10
    assert level10.damage_reaction_attack is not None
    assert level10.damage_reaction_attack.source_feature == "retaliation"

    assert build_rokhan_stonefury_level11_profile().level == 11
    survival = level11.progression_features.effect_bound_survival_save
    assert survival is not None
    assert survival.source_id == "relentless-rage"
    assert survival.required_effect_id == "rage"
    assert survival.initial_dc == 10 and survival.dc_increment == 5
    assert survival.replacement_hp == 22

    profile12 = build_rokhan_stonefury_level12_profile()
    assert profile12.level == 12
    assert profile12.final_ability_scores.constitution == 18
    assert level12.max_hp == 137
    assert level12.armor_class == 15
    assert level12.saving_throw_bonuses["constitution"] == 8

    registry = build_certified_hero_registry()
    for level in (10, 11, 12):
        assert ("barbarian", level, "canonical") in registry
