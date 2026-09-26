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
    _spell("guidance", "Guidance", "buff", "arena-out-of-scope", level=0, min_level=4),
    _spell("druidcraft", "Druidcraft", "utility", "arena-out-of-scope", level=0, min_level=10),
)

_PREPARED = (
    _spell("healing-word", "Healing Word", "healing", "healing", "bonus-action"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("longstrider", "Longstrider", "buff", "modifier-stack"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
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
