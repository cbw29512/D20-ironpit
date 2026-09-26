from __future__ import annotations

from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_2014_hunter_ranger_level_six_is_progression_only() -> None:
    hero = build_rowan_ashtrail_2014(6)
    profile = build_rowan_ashtrail_2014_profile(6)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert hero.level == 6
    assert hero.max_hp == 52
    assert hero.ability_scores.dexterity == 19
    assert hero.weapon_attack.attack_bonus == 9
    assert len(hero.attack_action.slots) == 2
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 2,
    }
    assert audits["favored-enemy-improvement-6"].combat_relevant is False
    assert audits["natural-explorer-improvement-6"].combat_relevant is False
