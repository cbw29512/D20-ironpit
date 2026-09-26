from __future__ import annotations

from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_fourteen_dragon_wings_uses_universal_movement_modes() -> None:
    hero = build_nyra_emberveil_2014(14)

    assert hero.level == 14
    assert hero.speed_ft == 30
    assert hero.movement_modes.walk_ft == 30
    assert hero.movement_modes.fly_ft == 30
    assert hero.movement_modes.hover is False


def test_level_fifteen_keeps_dragon_wings_and_progression_resources() -> None:
    hero = build_nyra_emberveil_2014(15)

    assert hero.movement_modes.fly_ft == 30
    assert {item.id: item.max_uses for item in hero.resources}["sorcery-points"] == 15
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-8"] == 1


def test_level_sixteen_constitution_asi_updates_hp_and_save() -> None:
    before = build_nyra_emberveil_2014(15)
    hero = build_nyra_emberveil_2014(16)
    profile = build_nyra_emberveil_2014_profile(16)

    assert profile.final_ability_scores.constitution == 16
    assert hero.max_hp > before.max_hp
    assert hero.saving_throw_bonuses["constitution"] == 8
    assert hero.movement_modes.fly_ft == 30
