from __future__ import annotations

from app.combat.spell_policy import spell_at_slot
from app.content.offensive_spell_effects import build_destructive_wave_2024, build_flame_strike_2024
from app.content.shared_damage_spells_2014 import flame_strike_2014
from app.content.storm_spell_effects import build_ice_storm_2024


def test_ice_storm_higher_slot_adds_printed_bludgeoning_only() -> None:
    spell = build_ice_storm_2024(16)
    scaled = spell_at_slot(spell, 6)
    assert [
        (part.dice_count, part.dice_size, part.damage_type)
        for part in scaled.damage_components
    ] == [(4, 10, "bludgeoning"), (4, 8, "cold")]


def test_flame_strike_2024_higher_slot_adds_both_printed_components() -> None:
    spell = build_flame_strike_2024(16)
    scaled = spell_at_slot(spell, 7)
    assert [
        (part.dice_count, part.dice_size, part.damage_type)
        for part in scaled.damage_components
    ] == [(7, 6, "fire"), (7, 6, "radiant")]


def test_flame_strike_2014_higher_slot_adds_printed_fire_only() -> None:
    spell = flame_strike_2014(16)
    scaled = spell_at_slot(spell, 6)
    assert [
        (part.dice_count, part.dice_size, part.damage_type)
        for part in scaled.damage_components
    ] == [(5, 6, "fire"), (4, 6, "radiant")]


def test_destructive_wave_has_no_printed_higher_slot_damage() -> None:
    spell = build_destructive_wave_2024(16)
    assert all(part.upcast_dice_per_level == 0 for part in spell.damage_components)
    assert spell.upcast_dice_per_level == 0
