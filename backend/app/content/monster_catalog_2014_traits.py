from __future__ import annotations

import re

from app.domain.traits import CombatTrait

MODELED_TRAITS = {
    "Pack Tactics": CombatTrait.PACK_TACTICS,
    "Swarm": CombatTrait.SWARM,
    "Undead Fortitude": CombatTrait.UNDEAD_FORTITUDE,
    "Magic Resistance": CombatTrait.MAGIC_RESISTANCE,
    "Magic Weapons": CombatTrait.MAGIC_WEAPONS,
    "Charge": CombatTrait.CHARGE,
}

ARENA_NEUTRAL_TRAITS = frozenset({
    "Agile", "Amphibious", "Beast of Burden", "False Appearance", "Flyby",
    "Hellish Restoration", "Hold Breath", "Ice Walk", "Illumination", "Jumper",
    "Keen Hearing", "Keen Hearing and Sight", "Keen Hearing and Smell", "Keen Sight",
    "Keen Smell", "Limited Amphibiousness", "Mimicry", "Running Leap", "Spider Climb",
    "Standing Leap", "Sunlight Sensitivity", "Training", "Water Breathing", "Web Walker",
})

SUPPORTED_TRAITS = frozenset(MODELED_TRAITS) | ARENA_NEUTRAL_TRAITS
_LEGENDARY_RESISTANCE = re.compile(r"^Legendary Resistance \((\d+)/Day\)$", re.I)


def legendary_resistance_uses_2014(names: list[str]) -> int:
    matches = [_LEGENDARY_RESISTANCE.match(name) for name in names]
    counts = [int(match.group(1)) for match in matches if match is not None]
    if len(counts) > 1:
        raise ValueError("Monster has multiple Legendary Resistance traits.")
    return counts[0] if counts else 0


def combat_traits_2014(names: list[str]) -> list[CombatTrait]:
    return [MODELED_TRAITS[name] for name in names if name in MODELED_TRAITS]


def unresolved_traits_2014(names: list[str]) -> list[str]:
    return [
        name for name in names
        if name not in SUPPORTED_TRAITS and _LEGENDARY_RESISTANCE.match(name) is None
    ]
