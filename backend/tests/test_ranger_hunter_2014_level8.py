from __future__ import annotations

from app.combat.state import build_combatant_state
from app.combat.debuff_counters import debuff_is_countered
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_eight_asi_and_lands_stride_reuse_shared_checks() -> None:
    hero = build_rowan_ashtrail_2014(8)
    profile = build_rowan_ashtrail_2014_profile(8)
    state = build_combatant_state(hero)

    assert hero.level == 8
    assert hero.ability_scores.dexterity == 20
    assert hero.ability_scores.wisdom == 15
    assert hero.armor_class == 16
    assert hero.initiative_bonus == 5
    assert hero.weapon_attack.attack_bonus == 10
    assert hero.weapon_attack.damage_bonus == 5

    lands_stride_save = next(
        item for item in hero.progression_features.saving_throw_advantage_grants
        if item.source_id == "lands-stride"
    )
    assert lands_stride_save.required_effect_tags == ["plant-impediment"]
    assert lands_stride_save.requires_magical_effect is True

    assert debuff_is_countered(
        state, "difficult-terrain", source_is_magical=False
    ) is True
    assert debuff_is_countered(
        state, "difficult-terrain", source_is_magical=True
    ) is False

    ids = {item.feature_id for item in profile.feature_audits}
    assert "ability-score-improvement-8" in ids
    assert "lands-stride" in ids


def test_level_eight_spell_progression_is_unchanged_from_level_seven() -> None:
    hero = build_rowan_ashtrail_2014(8)
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
    }
