from __future__ import annotations

import re

from app.domain.traits import CombatTrait

MODELED_TRAITS = {
    "Pack Tactics": CombatTrait.PACK_TACTICS,
    "Swarm": CombatTrait.SWARM,
    "Undead Fortitude": CombatTrait.UNDEAD_FORTITUDE,
    "Magic Resistance": CombatTrait.MAGIC_RESISTANCE,
    "Magic Weapons": CombatTrait.MAGIC_WEAPONS,
    "Sure-Footed": CombatTrait.SURE_FOOTED,
    "Charge": CombatTrait.CHARGE,
    "Pounce": CombatTrait.CHARGE,
    "Trampling Charge": CombatTrait.CHARGE,
}

DATA_BOUND_TRAITS = frozenset({
    "Blood Frenzy", "Echolocation", "Innate Spellcasting", "Spellcasting",
})

ARENA_NEUTRAL_TRAITS = frozenset({
    "Agile", "Amphibious", "Beast of Burden", "False Appearance", "Flyby",
    "Hellish Restoration", "Hold Breath", "Ice Walk", "Illumination", "Jumper",
    "Keen Hearing", "Keen Hearing and Sight", "Keen Hearing and Smell", "Keen Sight",
    "Keen Sight and Smell", "Keen Smell", "Limited Amphibiousness", "Mimicry", "Rejuvenation",
    "Running Leap", "Spider Climb", "Standing Leap", "Stone Camouflage", "Sunlight Sensitivity",
    "Training", "Water Breathing", "Web Walker",
})

SUPPORTED_TRAITS = frozenset(MODELED_TRAITS) | DATA_BOUND_TRAITS | ARENA_NEUTRAL_TRAITS
_LEGENDARY_RESISTANCE = re.compile(r"^Legendary Resistance \((\d+)/Day\)$", re.I)
_RELENTLESS = re.compile(r"^Relentless \(Recharges after a Short or Long Rest\)$", re.I)


def legendary_resistance_uses_2014(names: list[str]) -> int:
    matches = [_LEGENDARY_RESISTANCE.match(name) for name in names]
    counts = [int(match.group(1)) for match in matches if match is not None]
    if len(counts) > 1:
        raise ValueError("Monster has multiple Legendary Resistance traits.")
    return counts[0] if counts else 0


def combat_traits_2014(names: list[str]) -> list[CombatTrait]:
    return list(dict.fromkeys(MODELED_TRAITS[name] for name in names if name in MODELED_TRAITS))


def unresolved_traits_2014(names: list[str]) -> list[str]:
    return [
        name for name in names
        if name not in SUPPORTED_TRAITS
        and _LEGENDARY_RESISTANCE.match(name) is None
        and _RELENTLESS.match(name) is None
    ]
