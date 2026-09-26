from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_nineteen_asi_resources_and_spell_count() -> None:
    hero = build_rowan_ashtrail_2014(19)
    profile = build_rowan_ashtrail_2014_profile(19)
    package = build_ranger_2014_spell_package(19)

    assert profile.final_ability_scores.wisdom == 20
    assert profile.final_ability_scores.constitution == 15
    assert hero.max_hp == 156
    assert hero.weapon_attack.attack_bonus == 13
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
    }
    assert len(package.spells) == 11
    assert package.spells[-1].id == "tree-stride"
