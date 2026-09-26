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
    _spell("dancing-lights", "Dancing Lights", "utility", "arena-out-of-scope", level=0),
    _spell(
        "vicious-mockery", "Vicious Mockery", "mixed",
        "save-damage", "next-attack-disadvantage", level=0,
    ),
    _spell("mage-hand", "Mage Hand", "utility", "arena-out-of-scope", level=0, min_level=4),
    _spell("light", "Light", "utility", "arena-out-of-scope", level=0, min_level=10),
)

# One persistent Bard learns spells cumulatively. A Bard may replace one known
# spell on level-up, but this canonical support build does not need replacements:
# it appends legal choices in deterministic combat-first order. Magical Secrets
# entries at levels 10/14/18 count against Spells Known exactly as RAW requires.
_KNOWN = (
    _spell("healing-word", "Healing Word", "healing", "healing", "bonus-action"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("comprehend-languages", "Comprehend Languages", "utility", "arena-out-of-scope"),
    _spell("identify", "Identify", "utility", "arena-out-of-scope", min_level=2),
    _spell("animal-messenger", "Animal Messenger", "utility", "arena-out-of-scope", level=2, min_level=3),
    _spell(
        "lesser-restoration", "Lesser Restoration", "healing",
        "condition-removal", level=2, min_level=4,
    ),
    _spell("dispel-magic", "Dispel Magic", "control", "effect-removal", level=3, min_level=5),
    _spell("tongues", "Tongues", "utility", "arena-out-of-scope", level=3, min_level=6),
    _spell(
        "freedom-of-movement", "Freedom of Movement", "buff",
        "debuff-counter", "movement-cost-counter", level=4, min_level=7,
    ),
    _spell(
        "greater-invisibility", "Greater Invisibility", "buff",
        "condition", "concentration", level=4, min_level=8,
    ),
    _spell(
        "mass-cure-wounds", "Mass Cure Wounds", "healing",
        "multi-target-healing", level=5, min_level=9,
    ),
    _spell(
        "flame-strike", "Flame Strike", "damage",
        "save-damage", "area-damage", "multi-component-damage",
        "magical-secrets", level=5, min_level=10,
    ),
    _spell(
        "death-ward", "Death Ward", "buff",
        "zero-hp-replacement", "instant-death-prevention",
        "magical-secrets", level=4, min_level=10,
    ),
    _spell("find-the-path", "Find the Path", "utility", "arena-out-of-scope", level=6, min_level=11),
    _spell("project-image", "Project Image", "utility", "arena-out-of-scope", level=7, min_level=13),
    _spell(
        "harm", "Harm", "damage", "save-damage", "magical-secrets",
        level=6, min_level=14,
    ),
    _spell(
        "fire-storm", "Fire Storm", "damage", "save-damage", "area-effect",
        "magical-secrets", level=7, min_level=14,
    ),
    _spell("unseen-servant", "Unseen Servant", "utility", "arena-out-of-scope", level=1, min_level=15),
    _spell("illusory-script", "Illusory Script", "utility", "arena-out-of-scope", level=1, min_level=17),
    _spell(
        "aid", "Aid", "buff",
        "max-hp-increase", "magical-secrets", level=2, min_level=18,
    ),
    _spell(
        "spirit-guardians", "Spirit Guardians", "damage",
        "persistent-damage", "concentration", "magical-secrets",
        level=3, min_level=18,
    ),
)

# College of Lore Additional Magical Secrets at level 6 are bonus known spells
# and do not count against the Bard table's Spells Known column.
_ADDITIONAL_LORE_SECRETS = (
    _spell(
        "spiritual-weapon", "Spiritual Weapon", "damage",
        "persistent-spell-attack", "bonus-action", "additional-magical-secrets",
        level=2, min_level=6,
    ),
    _spell(
        "bless", "Bless", "buff",
        "modifier-stack", "concentration", "additional-magical-secrets",
        level=1, min_level=6,
    ),
)


def build_bard_2014_spell_package(level: int) -> ClassSpellPackage:
    try:
        if not 1 <= level <= 20:
            raise ValueError("2014 Bard level must be between 1 and 20.")
        from app.content.bard_2014_progression import bard_2014_level

        row = bard_2014_level(level)
        available = [spell for spell in _KNOWN if spell.min_character_level <= level]
        if len(available) != row.spells_known:
            raise ValueError(
                f"2014 Bard level {level} needs {row.spells_known} known spells; "
                f"the canonical package defines {len(available)}."
            )
        cantrips = [spell for spell in _CANTRIPS if spell.min_character_level <= level]
        if len(cantrips) != row.cantrips_known:
            raise ValueError(
                f"2014 Bard level {level} needs {row.cantrips_known} cantrips; "
                f"the canonical package defines {len(cantrips)}."
            )
        return ClassSpellPackage(
            class_id="bard",
            casting_ability="charisma",
            cantrips=cantrips,
            spells=available,
        )
    except Exception:
        logger.exception("Failed to build 2014 Bard spell package at level %s.", level)
        raise


def additional_lore_magical_secrets_2014(level: int) -> tuple[CanonicalSpellChoice, ...]:
    try:
        if not 1 <= level <= 20:
            raise ValueError("2014 Lore Bard level must be between 1 and 20.")
        return _ADDITIONAL_LORE_SECRETS if level >= 6 else ()
    except Exception:
        logger.exception("Failed to build 2014 Lore Bard Additional Magical Secrets at level %s.", level)
        raise
