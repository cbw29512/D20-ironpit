from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_nine_progression_and_spell_tier() -> None:
    hero = build_rowan_ashtrail_2014(9)
    package = build_ranger_2014_spell_package(9)

    assert hero.level == 9
    assert hero.max_hp == 76
    assert hero.weapon_attack.attack_bonus == 11
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
    }

    assert len(package.spells) == 6
    assert package.spells[-1].id == "daylight"
    assert package.spells[-1].spell_level == 3
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]
