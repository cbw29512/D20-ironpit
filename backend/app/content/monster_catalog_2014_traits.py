from __future__ import annotations

import re

from app.content.monster_catalog_2014_absorption import ABSORPTION_TRAITS_2014
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
    "Limited Magic Immunity": CombatTrait.LIMITED_MAGIC_IMMUNITY,
    "Magic Weapons": CombatTrait.MAGIC_WEAPONS,
    "Sure-Footed": CombatTrait.SURE_FOOTED,
    "Dark Devotion": CombatTrait.DARK_DEVOTION,
    "Brave": CombatTrait.BRAVE,
    "Two-Headed": CombatTrait.TWO_HEADED,
    "Two Heads": CombatTrait.TWO_HEADED,
    "Aggressive": CombatTrait.AGGRESSIVE,
    "Cunning Action": CombatTrait.CUNNING_ACTION,
    "Martial Advantage": CombatTrait.MARTIAL_ADVANTAGE,
    "Charge": CombatTrait.CHARGE,
    "Pounce": CombatTrait.CHARGE,
    "Trampling Charge": CombatTrait.CHARGE,
    "Rampage": CombatTrait.RAMPAGE,
    "Reactive": CombatTrait.REACTIVE,
}

DATA_BOUND_TRAITS = frozenset({
    "Angelic Weapons", "Aversion of Fire", "Barbed Hide", "Blood Frenzy", "Brute", "Echolocation", "Fear of Fire",
    "Heated Body", "Heated Weapons", "Innate Spellcasting", "Invisibility", "Petrifying Gaze", "Poor Depth Perception",
    "Reckless", "Regeneration", "Sneak Attack", "Sneak Attack (1/Turn)", "Spellcasting", "Stench", "Turning Defiance",
}) | ABSORPTION_TRAITS_2014

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
    traits = list(dict.fromkeys(item for item in modeled if item is not None))
    if CombatTrait.LIMITED_MAGIC_IMMUNITY in traits and CombatTrait.MAGIC_RESISTANCE not in traits:
        traits.append(CombatTrait.MAGIC_RESISTANCE)
    return traits


def unresolved_traits_2014(names: list[str], data_bound: list[str] | None = None) -> list[str]:
    supported = SUPPORTED_TRAITS | frozenset(data_bound or [])
    return [
        name for name in names
        if name not in supported
        and _modeled_trait(name) is None
        and _LEGENDARY_RESISTANCE.match(name) is None
        and _RELENTLESS.match(name) is None
    ]
