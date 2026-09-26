from __future__ import annotations

import logging

from app.domain.class_loadouts import CanonicalSpellChoice, ClassSpellPackage

logger = logging.getLogger(__name__)


def _spell(
    spell_id: str, name: str, role: str, *capabilities: str,
    level: int = 0, min_level: int = 1,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=level, min_character_level=min_level,
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
    _spell("comprehend-languages", "Comprehend Languages", "utility", "arena-out-of-scope", level=1),
    _spell("knock", "Knock", "utility", "arena-out-of-scope", level=2, min_level=3),
)


def build_sorcerer_2014_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level not in (1, 2, 3):
            raise ValueError("2014 Sorcerer spell package currently covers levels 1 through 3.")
        from app.content.sorcerer_2014_progression import sorcerer_2014_level

        row = sorcerer_2014_level(level)
        available = [spell for spell in _KNOWN if spell.min_character_level <= level]
        if len(available) < row.spells_known:
            raise ValueError(
                f"2014 Sorcerer level {level} needs {row.spells_known} known spells; "
                f"the canonical package defines {len(available)} legal choices."
            )
        return ClassSpellPackage(
            class_id="sorcerer", casting_ability="charisma",
            cantrips=list(_CANTRIPS[:row.cantrips_known]), spells=available[:row.spells_known],
        )
    except Exception:
        logger.exception("Failed to build 2014 Sorcerer spell package at level %s.", level)
        raise
