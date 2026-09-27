from __future__ import annotations

import logging

from app.domain.class_loadouts import CanonicalSpellChoice, ClassSpellPackage

logger = logging.getLogger(__name__)


def _spell(
    spell_id: str,
    name: str,
    role: str,
    *capabilities: str,
    level: int = 0,
    min_level: int = 1,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=level,
        min_character_level=min_level,
        role=role,
        required_capabilities=list(capabilities),
    )


_LEVEL_ONE_CANTRIPS = (
    _spell("eldritch-blast", "Eldritch Blast", "damage", "spell-attack"),
    _spell("poison-spray", "Poison Spray", "damage", "save-damage"),
)

_LEVEL_FOUR_CANTRIP = _spell(
    "mage-hand", "Mage Hand", "utility", min_level=4,
)

_LEVEL_ONE_KNOWN = (
    _spell("hex", "Hex", "damage", "targeted-concentration-damage", "concentration", level=1),
    _spell("burning-hands", "Burning Hands", "damage", "save-damage", "area", level=1),
)

_LEVEL_TWO_ADDITION = _spell(
    "comprehend-languages", "Comprehend Languages", "utility", level=1, min_level=2,
)

_LEVEL_THREE_DAMAGE = (
    _spell("scorching-ray", "Scorching Ray", "damage", "spell-attack", "multi-attack", level=2, min_level=3),
    _spell("shatter", "Shatter", "damage", "save-damage", "area", level=2, min_level=3),
)

_LEVEL_FOUR_UTILITY = _spell(
    "comprehend-languages", "Comprehend Languages", "utility", level=1, min_level=4,
)

_LEVEL_FIVE_DAMAGE = _spell(
    "fireball", "Fireball", "damage", "save-damage", "area", level=3, min_level=5,
)

_LEVEL_SIX_UTILITY = _spell(
    "dispel-magic", "Dispel Magic", "control", "effect-removal", level=3, min_level=6,
)

_LEVEL_SEVEN_UTILITY = _spell(
    "hallucinatory-terrain", "Hallucinatory Terrain", "utility", level=4, min_level=7,
)

_LEVEL_EIGHT_UTILITY = _spell(
    "dimension-door", "Dimension Door", "utility", level=4, min_level=8,
)

_LEVEL_NINE_DAMAGE = _spell(
    "flame-strike", "Flame Strike", "damage", "save-damage", "area", level=5, min_level=9,
)

_LEVEL_TEN_CANTRIP = _spell(
    "prestidigitation", "Prestidigitation", "utility", min_level=10,
)

_LEVEL_ELEVEN_KNOWN = _spell(
    "dream", "Dream", "utility", "arena-out-of-scope", level=5, min_level=11,
)

_LEVEL_ELEVEN_ARCANUM = _spell(
    "circle-of-death", "Circle of Death", "damage", "save-damage", "area", level=6, min_level=11,
)

_LEVEL_THIRTEEN_KNOWN = _spell(
    "scrying", "Scrying", "utility", "arena-out-of-scope", level=5, min_level=13,
)

_LEVEL_THIRTEEN_ARCANUM = _spell(
    "finger-of-death", "Finger of Death", "damage", "save-damage", level=7, min_level=13,
)

_LEVEL_FIFTEEN_KNOWN = _spell(
    "contact-other-plane", "Contact Other Plane", "utility", "arena-out-of-scope", level=5, min_level=15,
)

_LEVEL_FIFTEEN_ARCANUM = _spell(
    "power-word-stun", "Power Word Stun", "control", "hp-threshold-condition", level=8, min_level=15,
)


def build_warlock_2014_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level not in range(1, 17):
            raise ValueError("2014 Warlock canonical spell package currently certifies levels 1 through 16.")
        return ClassSpellPackage(
            class_id="warlock",
            casting_ability="charisma",
            cantrips=[
                *_LEVEL_ONE_CANTRIPS,
                *([_LEVEL_FOUR_CANTRIP] if level >= 4 else []),
                *([_LEVEL_TEN_CANTRIP] if level >= 10 else []),
            ],
            spells=[
                *_LEVEL_ONE_KNOWN,
                *([_LEVEL_TWO_ADDITION] if level == 2 else []),
                *(_LEVEL_THREE_DAMAGE if level >= 3 else []),
                *([_LEVEL_FOUR_UTILITY] if level >= 4 else []),
                *([_LEVEL_FIVE_DAMAGE] if level >= 5 else []),
                *([_LEVEL_SIX_UTILITY] if level >= 6 else []),
                *([_LEVEL_SEVEN_UTILITY] if level >= 7 else []),
                *([_LEVEL_EIGHT_UTILITY] if level >= 8 else []),
                *([_LEVEL_NINE_DAMAGE] if level >= 9 else []),
                *([_LEVEL_ELEVEN_KNOWN] if level >= 11 else []),
                *([_LEVEL_THIRTEEN_KNOWN] if level >= 13 else []),
                *([_LEVEL_FIFTEEN_KNOWN] if level >= 15 else []),
            ],
        )
    except Exception:
        logger.exception("Failed to build 2014 Warlock spell package at level %s.", level)
        raise
