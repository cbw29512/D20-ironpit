"""Tests for 2014 source reaction support classification."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_reactions_2014 import (
    supports_shield_reaction_2014,
    supports_spell_reflection_reaction_2014,
)


def test_shield_guardian_shield_reaction_source_verified():
    monsters = {m.name: m for m in load_monster_source_2014()}
    guardian = monsters["Shield Guardian"]
    assert supports_shield_reaction_2014(guardian)
    assert not supports_spell_reflection_reaction_2014(guardian)


def test_spectator_spell_reflection_source_verified():
    monsters = {m.name: m for m in load_monster_source_2014()}
    spectator = monsters["Spectator"]
    assert supports_spell_reflection_reaction_2014(spectator)
    assert not supports_shield_reaction_2014(spectator)
