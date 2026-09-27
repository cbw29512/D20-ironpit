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
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=level,
        min_character_level=1,
        role=role,
        required_capabilities=list(capabilities),
    )


_LEVEL_ONE_CANTRIPS = (
    _spell("eldritch-blast", "Eldritch Blast", "damage", "spell-attack"),
    _spell("poison-spray", "Poison Spray", "damage", "save-damage"),
)

_LEVEL_ONE_KNOWN = (
    _spell("hex", "Hex", "damage", "targeted-concentration-damage", "concentration", level=1),
    _spell("burning-hands", "Burning Hands", "damage", "save-damage", "area", level=1),
)


def build_warlock_2014_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level != 1:
            raise ValueError("2014 Warlock canonical spell package currently certifies level 1 only.")
        return ClassSpellPackage(
            class_id="warlock",
            casting_ability="charisma",
            cantrips=list(_LEVEL_ONE_CANTRIPS),
            spells=list(_LEVEL_ONE_KNOWN),
        )
    except Exception:
        logger.exception("Failed to build 2014 Warlock spell package at level %s.", level)
        raise
