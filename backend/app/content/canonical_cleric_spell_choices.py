from __future__ import annotations

import logging

from app.domain.class_loadouts import CanonicalSpellChoice

logger = logging.getLogger(__name__)


def _choice(
    spell_id: str,
    name: str,
    spell_level: int,
    min_character_level: int,
    role: str,
    *capabilities: str,
    always_prepared_from_level: int | None = None,
) -> CanonicalSpellChoice:
    try:
        return CanonicalSpellChoice(
            id=spell_id,
            name=name,
            spell_level=spell_level,
            min_character_level=min_character_level,
            always_prepared_from_level=always_prepared_from_level,
            role=role,
            required_capabilities=list(capabilities),
        )
    except Exception:
        logger.exception("Failed to define canonical Cleric spell %s.", spell_id)
        raise


CLERIC_CANTRIPS = (
    _choice("sacred-flame", "Sacred Flame", 0, 1, "damage", "save-damage", "cantrip-scaling"),
    _choice("light", "Light", 0, 1, "utility", "arena-out-of-scope"),
    _choice("thaumaturgy", "Thaumaturgy", 0, 1, "utility", "arena-out-of-scope"),
    _choice("mending", "Mending", 0, 4, "utility", "arena-out-of-scope"),
    _choice("spare-the-dying", "Spare the Dying", 0, 10, "healing", "arena-out-of-scope"),
)

CLERIC_SPELLS = (
    _choice("bless", "Bless", 1, 1, "buff", "modifier-stack", "concentration", always_prepared_from_level=3),
    _choice("cure-wounds", "Cure Wounds", 1, 1, "healing", "healing", always_prepared_from_level=3),
    _choice("guiding-bolt", "Guiding Bolt", 1, 1, "mixed", "spell-attack", "next-attack-advantage"),
    _choice("shield-of-faith", "Shield of Faith", 1, 1, "buff", "modifier-stack", "concentration"),
    _choice("healing-word", "Healing Word", 1, 2, "healing", "healing", "bonus-action"),
    _choice("detect-magic", "Detect Magic", 1, 3, "utility", "arena-out-of-scope"),
    _choice("create-or-destroy-water", "Create or Destroy Water", 1, 3, "utility", "arena-out-of-scope"),
    _choice("augury", "Augury", 2, 3, "utility", "arena-out-of-scope"),
    _choice("inflict-wounds", "Inflict Wounds", 1, 4, "damage", "save-damage"),
    _choice("aid", "Aid", 2, 3, "buff", "max-hp-increase", always_prepared_from_level=3),
    _choice(
        "lesser-restoration", "Lesser Restoration", 2, 3, "healing",
        "condition-removal", "bonus-action", always_prepared_from_level=3,
    ),
    _choice("dispel-magic", "Dispel Magic", 3, 5, "utility", "effect-removal"),
    _choice("create-food-and-water", "Create Food and Water", 3, 5, "utility", "arena-out-of-scope"),
    _choice("daylight", "Daylight", 3, 6, "utility", "arena-out-of-scope"),
    _choice(
        "mass-healing-word", "Mass Healing Word", 3, 5, "healing",
        "healing", "bonus-action", "multi-target-healing", always_prepared_from_level=5,
    ),
    _choice("revivify", "Revivify", 3, 5, "healing", "arena-out-of-scope", always_prepared_from_level=5),
    _choice("aura-of-life", "Aura of Life", 4, 7, "healing", "arena-out-of-scope", always_prepared_from_level=7),
    _choice("death-ward", "Death Ward", 4, 7, "healing", "arena-out-of-scope", always_prepared_from_level=7),
    _choice("prayer-of-healing", "Prayer of Healing", 2, 7, "healing", "arena-out-of-scope"),
    _choice("guardian-of-faith", "Guardian of Faith", 4, 8, "damage", "arena-out-of-scope"),
    _choice("flame-strike", "Flame Strike", 5, 9, "damage", "arena-out-of-scope"),
    _choice("insect-plague", "Insect Plague", 5, 9, "damage", "arena-out-of-scope"),
    _choice("contagion", "Contagion", 5, 10, "damage", "arena-out-of-scope"),
    _choice("heal", "Heal", 6, 11, "healing", "arena-out-of-scope"),
    _choice(
        "greater-restoration", "Greater Restoration", 5, 9, "healing",
        "arena-out-of-scope", always_prepared_from_level=9,
    ),
    _choice(
        "mass-cure-wounds", "Mass Cure Wounds", 5, 9, "healing",
        "healing", "multi-target-healing", always_prepared_from_level=9,
    ),
)
