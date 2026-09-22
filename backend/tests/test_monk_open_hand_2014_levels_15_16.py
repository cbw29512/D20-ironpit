from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_entries_for_ruleset
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014


def test_level15_timeless_body_is_explicitly_arena_neutral() -> None:
    hero14 = build_kael_stillwater_2014(14)
    hero15 = build_kael_stillwater_2014(15)
    profile15 = build_kael_stillwater_2014_profile(15)

    timeless = next(item for item in profile15.feature_audits if item.feature_id == "timeless-body")
    assert timeless.combat_relevant is False
    assert timeless.automated is False
    assert hero15.ability_scores == hero14.ability_scores
    assert hero15.armor_class == hero14.armor_class
    assert hero15.progression_features == hero14.progression_features
    assert hero15.max_hp == hero14.max_hp + 7
    assert next(item for item in hero15.resources if item.id == "ki").max_uses == 15


def test_level16_is_pure_wisdom_asi_delta_on_top_of_diamond_soul() -> None:
    hero15 = build_kael_stillwater_2014(15)
    hero16 = build_kael_stillwater_2014(16)
    profile16 = build_kael_stillwater_2014_profile(16)
    fingerprint16 = build_kael_2014_combat_profile(16)

    assert hero16.ability_scores is not None
    assert hero16.ability_scores.wisdom == 19
    assert hero16.ability_scores.dexterity == 20
    assert hero16.armor_class == 19
    assert hero16.max_hp == hero15.max_hp + 7
    assert hero16.speed_ft == 55
    assert hero16.saving_throw_bonuses == {
        "strength": 6,
        "dexterity": 10,
        "constitution": 7,
        "intelligence": 5,
        "wisdom": 9,
        "charisma": 4,
    }
    assert hero16.progression_features.failed_save_reroll_grants == (
        hero15.progression_features.failed_save_reroll_grants
    )
    assert next(item for item in hero16.resources if item.id == "ki").max_uses == 16

    asi = next(item for item in profile16.feature_audits if item.feature_id == "ability-score-improvement-l16")
    assert asi.combat_relevant is True
    assert asi.automated is True
    assert profile16.final_ability_scores.wisdom == 19
    assert fingerprint16.abilities.wisdom == 19
    assert fingerprint16.armor_class == 19


def test_2014_monk_registry_now_reaches_level16() -> None:
    registry = {
        key: (template.name, template.id)
        for key, template in build_certified_hero_entries_for_ruleset("2014")
    }
    for level in range(1, 17):
        assert registry[("monk", level, "canonical-2014")] == (
            "Kael Stillwater",
            f"kael-stillwater-2014-l{level}",
        )
