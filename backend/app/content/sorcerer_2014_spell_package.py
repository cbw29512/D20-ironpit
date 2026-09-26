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
    _spell("message", "Message", "utility", "arena-out-of-scope"),
    _spell("minor-illusion", "Minor Illusion", "utility", "arena-out-of-scope", min_level=10),
)

_KNOWN = (
    _spell("burning-hands", "Burning Hands", "damage", "save-damage", "area", level=1),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope", level=1),
    _spell("comprehend-languages", "Comprehend Languages", "utility", "arena-out-of-scope", level=1),
    _spell("knock", "Knock", "utility", "arena-out-of-scope", level=2, min_level=3),
    _spell("detect-thoughts", "Detect Thoughts", "utility", "arena-out-of-scope", level=2, min_level=4),
    _spell("fireball", "Fireball", "damage", "save-damage", "area", level=3, min_level=5),
    _spell("clairvoyance", "Clairvoyance", "utility", "arena-out-of-scope", level=3, min_level=6),
    _spell("greater-invisibility", "Greater Invisibility", "buff", "condition", "concentration", level=4, min_level=7),
    _spell("dispel-magic", "Dispel Magic", "control", "effect-removal", level=3, min_level=8),
    _spell("creation", "Creation", "utility", "arena-out-of-scope", level=5, min_level=9),
    _spell("teleportation-circle", "Teleportation Circle", "utility", "arena-out-of-scope", level=5, min_level=10),
    _spell("move-earth", "Move Earth", "utility", "arena-out-of-scope", level=6, min_level=11),
    _spell("teleport", "Teleport", "utility", "arena-out-of-scope", level=7, min_level=13),
    _spell("tongues", "Tongues", "utility", "arena-out-of-scope", level=3, min_level=15),
    _spell("water-breathing", "Water Breathing", "utility", "arena-out-of-scope", level=3, min_level=17),
)


def build_sorcerer_2014_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Sorcerer spell package currently covers levels 1 through 20.")
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
