from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_seven_adds_fourth_level_slot_and_greater_invisibility() -> None:
    hero = build_nyra_emberveil_2014(7)
    profile = build_nyra_emberveil_2014_profile(7)
    package = build_sorcerer_2014_spell_package(7)

    assert hero.level == 7
    assert profile.level == 7
    assert hero.max_hp == 37
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
        "sorcery-points": 7,
    }
    assert len(package.spells) == 8
    assert package.spells[-1].id == "greater-invisibility"

    spell = next(item for item in hero.defensive_spell_actions if item.id == "greater-invisibility")
    assert spell.level == 4
    assert spell.concentration is True
    assert spell.condition_ids == ["invisible"]
    assert spell.duration_minutes == 1
