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
    min_level: int = 2,
    oath_level: int | None = None,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=level,
        min_character_level=min_level,
        always_prepared_from_level=oath_level,
        role=role,
        required_capabilities=list(capabilities),
    )


_PREPARED = (
    _spell("bless", "Bless", "buff", "modifier-stack", "concentration"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("shield-of-faith", "Shield of Faith", "buff", "modifier-stack", "concentration", "bonus-action"),
    _spell("heroism", "Heroism", "buff", "modifier-stack", "concentration"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("detect-evil-and-good", "Detect Evil and Good", "utility", "arena-out-of-scope"),
    _spell("purify-food-and-drink", "Purify Food and Drink", "utility", "arena-out-of-scope"),
    _spell("detect-poison-and-disease", "Detect Poison and Disease", "utility", "arena-out-of-scope"),
)

_OATH = (
    _spell(
        "protection-from-evil-and-good", "Protection from Evil and Good", "buff",
        "typed-defense", "condition-immunity", "concentration", oath_level=3, min_level=3,
    ),
    _spell("sanctuary", "Sanctuary", "buff", "attack-gate-save", "bonus-action", oath_level=3, min_level=3),
    _spell(
        "lesser-restoration", "Lesser Restoration", "healing", "condition-removal",
        level=2, min_level=5, oath_level=5,
    ),
    _spell("zone-of-truth", "Zone of Truth", "control", "arena-out-of-scope", level=2, min_level=5, oath_level=5),
    _spell(
        "beacon-of-hope", "Beacon of Hope", "buff", "healing-maximize", "death-save-advantage", "concentration",
        level=3, min_level=9, oath_level=9,
    ),
    _spell("dispel-magic", "Dispel Magic", "utility", "effect-removal", level=3, min_level=9, oath_level=9),
)


def prepared_count_2014(level: int, charisma_modifier: int) -> int:
    try:
        if not 1 <= level <= 20:
            raise ValueError("2014 Paladin level must be between 1 and 20.")
        if level < 2:
            return 0
        return max(1, charisma_modifier + level // 2)
    except Exception:
        logger.exception("Failed to calculate 2014 Paladin prepared spell count at level %s", level)
        raise


def build_paladin_2014_spell_package(level: int, charisma_modifier: int) -> ClassSpellPackage | None:
    try:
        count = prepared_count_2014(level, charisma_modifier)
        if count == 0:
            return None
        if count > len(_PREPARED):
            raise ValueError(
                f"2014 Paladin canonical spell package needs {count} prepared spells but defines {len(_PREPARED)}."
            )
        oath = [spell for spell in _OATH if spell.always_prepared_from_level and level >= spell.always_prepared_from_level]
        return ClassSpellPackage(
            class_id="paladin",
            casting_ability="charisma",
            spells=list(_PREPARED[:count]),
            always_prepared_spells=oath,
        )
    except Exception:
        logger.exception("Failed to build 2014 Paladin spell package at level %s", level)
        raise
