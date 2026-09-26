from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_nine_adds_fifth_level_slot_and_tenth_known_spell() -> None:
    hero = build_nyra_emberveil_2014(9)
    package = build_sorcerer_2014_spell_package(9)

    assert hero.level == 9
    assert hero.max_hp == 56
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 1,
        "sorcery-points": 9,
    }
    assert len(package.spells) == 10
    assert package.spells[-1].id == "creation"

    fire_bolt = next(item for item in hero.spell_attack_actions if item.id == "fire-bolt")
    fireball = next(item for item in hero.spell_save_actions if item.id == "fireball")
    assert fire_bolt.attack_bonus == 9
    assert fireball.dc == 17
