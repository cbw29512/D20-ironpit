from __future__ import annotations

from app.content.canonical_spell_policy import canonical_spell_package
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_2014_hunter_ranger_level_five_extra_attack_and_slots() -> None:
    hero = build_rowan_ashtrail_2014(5)

    assert hero.level == 5
    assert hero.max_hp == 44
    assert hero.ability_scores.dexterity == 19
    assert hero.weapon_attack.attack_bonus == 9
    assert hero.weapon_attack.damage_bonus == 4
    assert hero.attack_action is not None
    assert hero.attack_action.id == "extra-attack"
    assert len(hero.attack_action.slots) == 2
    assert all(
        slot.attack_ids == ["rowan-2014-longbow", "rowan-2014-shortsword"]
        for slot in hero.attack_action.slots
    )
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 2,
    }


def test_2014_hunter_ranger_level_five_reuses_lesser_restoration() -> None:
    hero = build_rowan_ashtrail_2014(5)
    package = canonical_spell_package("ranger", 5, "2014")

    assert [item.id for item in hero.condition_removal_actions] == ["lesser-restoration"]
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "longstrider", "cure-wounds", "detect-magic", "lesser-restoration",
    ]
