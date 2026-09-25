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


_DEATH_WARD = _spell(
    "death-ward", "Death Ward", "buff",
    "zero-hp-replacement", "instant-death-prevention",
    level=4, min_level=13,
)

_PREPARED = (
    _spell("bless", "Bless", "buff", "modifier-stack", "concentration"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("shield-of-faith", "Shield of Faith", "buff", "modifier-stack", "concentration", "bonus-action"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("detect-evil-and-good", "Detect Evil and Good", "utility", "arena-out-of-scope"),
    _spell("purify-food-and-drink", "Purify Food and Drink", "utility", "arena-out-of-scope"),
    _spell("detect-poison-and-disease", "Detect Poison and Disease", "utility", "arena-out-of-scope"),
    _spell("aid", "Aid", "buff", "max-hp-increase", level=2, min_level=5),
    # RAW 2014 Paladins can prepare Magic Weapon once 2nd-level slots are available.
    # It reuses the universal modifier-stack + concentration capabilities rather than
    # introducing spell-specific engine behavior, and supplies the ninth prepared
    # spell required by Aurelia's level-12 CHA modifier + half-level preparation count.
    _spell("magic-weapon", "Magic Weapon", "buff", "modifier-stack", "concentration", level=2, min_level=5),
    _spell("divine-favor", "Divine Favor", "buff", "modifier-stack", "bonus-damage", "concentration"),
    # Level 16 raises Aurelia's prepared-spell capacity to 12. These two legal 2014 Paladin spells
    # fill the additional preparation slots without inventing combat behavior: Find Steed is governed
    # by the global no-summons arena rule, while Create Food and Water cannot alter a Pit fight.
    _spell("find-steed", "Find Steed", "utility", "arena-unavailable-summon", level=2, min_level=5),
    _spell("create-food-and-water", "Create Food and Water", "utility", "arena-out-of-scope", level=3, min_level=9),
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
        "beacon-of-hope", "Beacon of Hope", "buff", "saving-throw-advantage", "healing-maximize", "death-save-advantage", "concentration",
        level=3, min_level=9, oath_level=9,
    ),
    _spell("dispel-magic", "Dispel Magic", "utility", "effect-removal", level=3, min_level=9, oath_level=9),
    _spell(
        "freedom-of-movement", "Freedom of Movement", "buff",
        "debuff-counter", "movement-cost-counter",
        level=4, min_level=13, oath_level=13,
    ),
    _spell(
        "guardian-of-faith", "Guardian of Faith", "control",
        "arena-unavailable-summon",
        level=4, min_level=13, oath_level=13,
    ),
    _spell("commune", "Commune", "utility", "arena-out-of-scope", level=5, min_level=17, oath_level=17),
    _spell(
        "flame-strike", "Flame Strike", "damage",
        "save-damage", "area-damage", "multi-component-damage",
        level=5, min_level=17, oath_level=17,
    ),
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
        prepared = list(_PREPARED[:count])
        if level >= 13:
            prepared = [spell for spell in prepared if spell.id != "purify-food-and-drink"]
            prepared.append(_DEATH_WARD)
        oath = [spell for spell in _OATH if spell.always_prepared_from_level and level >= spell.always_prepared_from_level]
        return ClassSpellPackage(
            class_id="paladin",
            casting_ability="charisma",
            spells=prepared,
            always_prepared_spells=oath,
        )
    except Exception:
        logger.exception("Failed to build 2014 Paladin spell package at level %s", level)
        raise
