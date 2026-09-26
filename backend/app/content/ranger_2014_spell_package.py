from __future__ import annotations

import logging

from app.domain.class_loadouts import CanonicalSpellChoice, ClassSpellPackage

logger = logging.getLogger(__name__)

_SPELLS = (
    CanonicalSpellChoice(
        id="longstrider", name="Longstrider", spell_level=1, min_character_level=2,
        role="buff", required_capabilities=["modifier-stack"],
    ),
    CanonicalSpellChoice(
        id="cure-wounds", name="Cure Wounds", spell_level=1, min_character_level=2,
        role="healing", required_capabilities=["healing"],
    ),
    CanonicalSpellChoice(
        id="detect-magic", name="Detect Magic", spell_level=1, min_character_level=3,
        role="utility", required_capabilities=["arena-out-of-scope"],
    ),
    CanonicalSpellChoice(
        id="lesser-restoration", name="Lesser Restoration", spell_level=2, min_character_level=5,
        role="healing", required_capabilities=["condition-removal"],
    ),
    CanonicalSpellChoice(
        id="locate-object", name="Locate Object", spell_level=2, min_character_level=7,
        role="utility", required_capabilities=["arena-out-of-scope"],
    ),
    CanonicalSpellChoice(
        id="daylight", name="Daylight", spell_level=3, min_character_level=9,
        role="utility", required_capabilities=["arena-out-of-scope"],
    ),
    CanonicalSpellChoice(
        id="water-walk", name="Water Walk", spell_level=3, min_character_level=11,
        role="utility", required_capabilities=["arena-out-of-scope"],
    ),
    CanonicalSpellChoice(
        id="freedom-of-movement", name="Freedom of Movement", spell_level=4, min_character_level=13,
        role="buff", required_capabilities=["debuff-counter"],
    ),
    CanonicalSpellChoice(
        id="locate-creature", name="Locate Creature", spell_level=4, min_character_level=15,
        role="utility", required_capabilities=["arena-out-of-scope"],
    ),
)


def build_ranger_2014_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level not in range(2, 21):
            raise ValueError("2014 Ranger spellcasting covers levels 2 through 20.")
        from app.content.ranger_2014_progression import ranger_2014_level

        row = ranger_2014_level(level)
        available = [spell for spell in _SPELLS if spell.min_character_level <= level]
        if row.spells_known > len(available):
            raise ValueError(
                f"2014 Ranger level {level} needs {row.spells_known} known spells; "
                f"the canonical package currently defines {len(available)} legal choices."
            )
        return ClassSpellPackage(
            class_id="ranger", casting_ability="wisdom",
            cantrips=[], spells=available[:row.spells_known],
        )
    except Exception:
        logger.exception("Failed to build 2014 Ranger spell package at level %s.", level)
        raise
