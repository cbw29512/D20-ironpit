"""Bind 2014 monster prepared spells to the *existing* hero spell actions.

This is a source-validated adapter, not a monster-specific spell resolver.
Only known combat spells are returned; callers must keep other printed spells
visible and must not certify incomplete monster spell lists.
"""
from __future__ import annotations

from app.content.cleric_2014_level1_spells import (
    bless_2014, cure_wounds_2014, sacred_flame_2014,
)
from app.content.shared_spells_2014 import sanctuary_2014
from app.content.monster_definition_adapter_support_2014 import ability_values_2014

# Printed utility cantrips: retain in source/card, but no action in standard arena.
_ARENA_NEUTRAL_2014 = frozenset({"light", "thaumaturgy"})


def prepared_spell_actions_2014(monster):
    source = monster.spellcasting
    if source is None:
        return {"spell_save_actions": [], "healing_actions": [],
                "defensive_spell_actions": [], "unbound_spell_ids": [],
                "arena_neutral_spell_ids": []}
    if not isinstance(source, dict) or source.get("source_complete") is not True:
        raise ValueError(f"{monster.name}: prepared spell source is incomplete")
    spells = source.get("spells")
    if not isinstance(spells, list) or not spells:
        raise ValueError(f"{monster.name}: prepared spell list is missing")
    wisdom = ability_values_2014(monster)["wisdom"]
    if type(wisdom) is not int or not 1 <= wisdom <= 30:
        raise ValueError(f"{monster.name}: invalid Wisdom for cleric spell binding")
    wisdom_mod = (wisdom - 10) // 2
    dc = source.get("save_dc")
    if type(dc) is not int or not 1 <= dc <= 40:
        raise ValueError(f"{monster.name}: missing printed spell save DC")

    actions = {"spell_save_actions": [], "healing_actions": [],
               "defensive_spell_actions": [], "unbound_spell_ids": [],
               "arena_neutral_spell_ids": []}
    seen = set()
    for entry in spells:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ValueError(f"{monster.name}: malformed prepared spell")
        spell_id = entry["id"]
        if spell_id in seen:
            raise ValueError(f"{monster.name}: duplicate prepared spell {spell_id}")
        seen.add(spell_id)
        if spell_id == "sacred-flame":
            actions["spell_save_actions"].append(sacred_flame_2014(dc))
        elif spell_id == "cure-wounds":
            actions["healing_actions"].append(cure_wounds_2014(wisdom_mod, 0))
        elif spell_id == "bless":
            actions["defensive_spell_actions"].append(bless_2014())
        elif spell_id == "sanctuary":
            actions["defensive_spell_actions"].append(sanctuary_2014(dc))
        elif spell_id in _ARENA_NEUTRAL_2014 and entry.get("level") == 0:
            actions["arena_neutral_spell_ids"].append(spell_id)
        else:
            actions["unbound_spell_ids"].append(spell_id)
    return actions
