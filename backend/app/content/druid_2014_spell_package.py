from __future__ import annotations

import logging

from app.domain.class_loadouts import CanonicalSpellChoice, ClassSpellPackage

logger = logging.getLogger(__name__)


def _spell(
    spell_id: str,
    name: str,
    role: str,
    *capabilities: str,
    level: int = 1,
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


_CANTRIPS = (
    _spell("produce-flame", "Produce Flame", "damage", "spell-attack", "cantrip-scaling", level=0),
    _spell("poison-spray", "Poison Spray", "damage", "save-damage", "cantrip-scaling", level=0),
    _spell("druidcraft", "Druidcraft", "utility", "arena-out-of-scope", level=0, min_level=4),
    _spell("guidance", "Guidance", "buff", "arena-out-of-scope", level=0, min_level=10),
)

_PREPARED = (
    _spell("healing-word", "Healing Word", "healing", "healing", "bonus-action"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("longstrider", "Longstrider", "buff", "modifier-stack"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell(
        "faerie-fire", "Faerie Fire", "control",
        "save-modifier", "area-effect", "concentration", min_level=2,
    ),
    _spell(
        "lesser-restoration", "Lesser Restoration", "healing",
        "condition-removal", level=2, min_level=3,
    ),
    _spell(
        "darkvision", "Darkvision", "utility",
        "arena-out-of-scope", level=2, min_level=4,
    ),
    _spell(
        "locate-animals-or-plants", "Locate Animals or Plants", "utility",
        "arena-out-of-scope", level=2, min_level=4,
    ),
    _spell(
        "dispel-magic", "Dispel Magic", "control",
        "effect-removal", level=3, min_level=5,
    ),
    _spell(
        "water-breathing", "Water Breathing", "utility",
        "arena-out-of-scope", level=3, min_level=6,
    ),
    _spell(
        "water-walk", "Water Walk", "utility",
        "arena-out-of-scope", level=3, min_level=7,
    ),
    _spell(
        "control-water", "Control Water", "utility",
        "arena-out-of-scope", level=4, min_level=8,
    ),
    _spell(
        "locate-creature", "Locate Creature", "utility",
        "arena-out-of-scope", level=4, min_level=8,
    ),
    _spell(
        "reincarnate", "Reincarnate", "utility",
        "arena-out-of-scope", level=5, min_level=9,
    ),
    _spell(
        "scrying", "Scrying", "utility",
        "arena-out-of-scope", level=5, min_level=10,
    ),
    _spell(
        "find-the-path", "Find the Path", "utility",
        "arena-out-of-scope", level=6, min_level=11,
    ),
    _spell(
        "wind-walk", "Wind Walk", "utility",
        "arena-out-of-scope", level=6, min_level=12,
    ),
    _spell(
        "mirage-arcane", "Mirage Arcane", "utility",
        "arena-out-of-scope", level=7, min_level=13,
    ),
    _spell(
        "transport-via-plants", "Transport via Plants", "utility",
        "arena-out-of-scope", level=6, min_level=14,
    ),
)


def prepared_count_2014(level: int, wisdom_modifier: int) -> int:
    try:
        if not 1 <= level <= 20:
            raise ValueError("2014 Druid level must be between 1 and 20.")
        return max(1, level + wisdom_modifier)
    except Exception:
        logger.exception("Failed to compute 2014 Druid prepared-spell count at level %s.", level)
        raise


def build_druid_2014_spell_package(level: int, wisdom_modifier: int) -> ClassSpellPackage:
    try:
        from app.content.druid_2014_progression import druid_2014_level

        row = druid_2014_level(level)
        count = prepared_count_2014(level, wisdom_modifier)
        available = [spell for spell in _PREPARED if spell.min_character_level <= level]
        if count > len(available):
            raise ValueError(
                f"2014 Druid level {level} needs {count} prepared spells; "
                f"the canonical package currently defines {len(available)} legal choices."
            )
        cantrips = [spell for spell in _CANTRIPS if spell.min_character_level <= level]
        if len(cantrips) != row.cantrips_known:
            raise ValueError(
                f"2014 Druid level {level} needs {row.cantrips_known} cantrips; "
                f"the canonical package defines {len(cantrips)}."
            )
        return ClassSpellPackage(
            class_id="druid",
            casting_ability="wisdom",
            cantrips=cantrips,
            spells=available[:count],
        )
    except Exception:
        logger.exception("Failed to build 2014 Druid spell package at level %s.", level)
        raise
