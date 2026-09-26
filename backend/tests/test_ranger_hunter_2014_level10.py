from __future__ import annotations

from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_ten_progression_and_arena_neutral_hide_in_plain_sight() -> None:
    hero = build_rowan_ashtrail_2014(10)
    profile = build_rowan_ashtrail_2014_profile(10)

    assert hero.level == 10
    assert hero.max_hp == 84
    assert hero.weapon_attack.attack_bonus == 11
    assert hero.weapon_attack.damage_bonus == 5
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
    }

    hide = next(item for item in profile.feature_audits if item.feature_id == "hide-in-plain-sight")
    assert hide.combat_relevant is False
    assert hide.automated is False

    explorer = next(
        item for item in profile.feature_audits
        if item.feature_id == "natural-explorer-improvement-10"
    )
    assert explorer.combat_relevant is False
    assert explorer.automated is True
