from __future__ import annotations

import re

from app.content.monster_catalog_2014_arena_policy import (
    ARENA_OUT_OF_SCOPE_TRAITS_2014,
    ARENA_USABLE_MOVEMENT_TRAITS_2014,
)
from app.domain.traits import CombatTrait

MODELED_TRAITS = {
    "Pack Tactics": CombatTrait.PACK_TACTICS,
    "Swarm": CombatTrait.SWARM,
    "Undead Fortitude": CombatTrait.UNDEAD_FORTITUDE,
    "Magic Resistance": CombatTrait.MAGIC_RESISTANCE,
    "Magic Weapons": CombatTrait.MAGIC_WEAPONS,
    "Sure-Footed": CombatTrait.SURE_FOOTED,
    "Dark Devotion": CombatTrait.DARK_DEVOTION,
    "Two-Headed": CombatTrait.TWO_HEADED,
    "Aggressive": CombatTrait.AGGRESSIVE,
    "Martial Advantage": CombatTrait.MARTIAL_ADVANTAGE,
    "Charge": CombatTrait.CHARGE,
    "Pounce": CombatTrait.CHARGE,
    "Trampling Charge": CombatTrait.CHARGE,
    "Rampage": CombatTrait.RAMPAGE,
}

DATA_BOUND_TRAITS = frozenset({
    "Angelic Weapons", "Barbed Hide", "Blood Frenzy", "Echolocation", "Fear of Fire", "Fire Absorption",
    "Heated Body", "Heated Weapons", "Innate Spellcasting", "Invisibility", "Petrifying Gaze", "Poor Depth Perception",
    "Reckless", "Regeneration", "Spellcasting", "Stench", "Turning Defiance",
})

ARENA_NEUTRAL_TRAITS = frozenset({
    "Agile", "Amorphous", "Amphibious", "Antimagic Susceptibility", "Beast of Burden", "Blind Senses",
    "Devil's Sight", "Flyby", "Hold Breath", "Ice Walk", "Illumination", "Immutable Form", "Jumper",
    "Keen Hearing", "Keen Hearing and Sight", "Keen Hearing and Smell", "Keen Sight",
    "Keen Sight and Smell", "Keen Smell", "Labyrinthine Recall", "Limited Amphibiousness",
    "Nimble Escape", "Running Leap", "Shark Telepathy", "Shapechanger", "Snow Camouflage", "Standing Leap",
    "Stone Camouflage", "Sunlight Sensitivity", "Training", "Water Breathing",
}) | ARENA_OUT_OF_SCOPE_TRAITS_2014 | ARENA_USABLE_MOVEMENT_TRAITS_2014

SUPPORTED_TRAITS = frozenset(MODELED_TRAITS) | DATA_BOUND_TRAITS | ARENA_NEUTRAL_TRAITS
_LEGENDARY_RESISTANCE = re.compile(r"^Legendary Resistance \((\d+)/Day\)$", re.I)
_RELENTLESS = re.compile(r"^Relentless \(Recharges after a Short or Long Rest\)$", re.I)
_FORM_ONLY_SUFFIX = re.compile(r"\s*\([^)]*form only\)$", re.I)


def _modeled_trait(name: str) -> CombatTrait | None:
    """Resolve modeled traits while preserving source form qualifiers in the catalog."""
    return MODELED_TRAITS.get(name) or MODELED_TRAITS.get(_FORM_ONLY_SUFFIX.sub("", name))


def legendary_resistance_uses_2014(names: list[str]) -> int:
    matches = [_LEGENDARY_RESISTANCE.match(name) for name in names]
    counts = [int(match.group(1)) for match in matches if match is not None]
    if len(counts) > 1: raise ValueError("Monster has multiple Legendary Resistance traits.")
    return counts[0] if counts else 0


def combat_traits_2014(names: list[str]) -> list[CombatTrait]:
    modeled = [_modeled_trait(name) for name in names]
    return list(dict.fromkeys(item for item in modeled if item is not None))


def unresolved_traits_2014(names: list[str], data_bound: list[str] | None = None) -> list[str]:
    supported = SUPPORTED_TRAITS | frozenset(data_bound or [])
    return [
        name for name in names
        if name not in supported
        and _modeled_trait(name) is None
        and _LEGENDARY_RESISTANCE.match(name) is None
        and _RELENTLESS.match(name) is None
    ]
