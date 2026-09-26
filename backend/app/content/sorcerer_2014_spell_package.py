from __future__ import annotations

import logging

from app.domain.class_loadouts import CanonicalSpellChoice, ClassSpellPackage

logger = logging.getLogger(__name__)


def _spell(spell_id: str, name: str, role: str, *capabilities: str, level: int = 0) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=level, min_character_level=1,
        role=role, required_capabilities=list(capabilities),
    )


_CANTRIPS = (
    _spell("fire-bolt", "Fire Bolt", "damage", "spell-attack"),
    _spell("light", "Light", "utility", "arena-out-of-scope"),
    _spell("mage-hand", "Mage Hand", "utility", "arena-out-of-scope"),
    _spell("prestidigitation", "Prestidigitation", "utility", "arena-out-of-scope"),
)

_KNOWN = (
    _spell("burning-hands", "Burning Hands", "damage", "save-damage", "area", level=1),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope", level=1),
)


def build_sorcerer_2014_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level != 1:
            raise ValueError("2014 Sorcerer spell package currently covers level 1.")
        return ClassSpellPackage(
            class_id="sorcerer", casting_ability="charisma",
            cantrips=list(_CANTRIPS), spells=list(_KNOWN),
        )
    except Exception:
        logger.exception("Failed to build 2014 Sorcerer spell package at level %s.", level)
        raise
