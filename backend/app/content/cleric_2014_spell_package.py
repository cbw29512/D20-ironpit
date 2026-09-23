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
    domain_level: int | None = None,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=level,
        min_character_level=min_level,
        always_prepared_from_level=domain_level,
        role=role,
        required_capabilities=list(capabilities),
    )


_CANTRIPS = (
    _spell("guidance", "Guidance", "buff", "arena-out-of-scope", level=0),
    _spell("sacred-flame", "Sacred Flame", "damage", "save-damage", "cantrip-scaling", level=0),
    _spell("spare-the-dying", "Spare the Dying", "healing", "stabilization", level=0),
)

# Prepared choices belong to the one persistent character. New levels extend this
# ordered package; they do not replace Seraphine's prior spell choices.
_PREPARED = (
    _spell("healing-word", "Healing Word", "healing", "healing", "bonus-action"),
    _spell("guiding-bolt", "Guiding Bolt", "mixed", "spell-attack", "next-attack-advantage"),
    _spell("shield-of-faith", "Shield of Faith", "buff", "modifier-stack", "concentration"),
    _spell("inflict-wounds", "Inflict Wounds", "damage", "spell-attack"),
    _spell("sanctuary", "Sanctuary", "buff", "attack-gate-save", "bonus-action"),
    _spell("hold-person", "Hold Person", "control", "condition", "repeat-save", level=2, min_level=3),
    _spell("prayer-of-healing", "Prayer of Healing", "healing", "arena-out-of-scope", level=2, min_level=3),
    _spell("silence", "Silence", "control", "area-effect", "concentration", level=2, min_level=3),
)

_DOMAIN = (
    _spell("bless", "Bless", "buff", "modifier-stack", "concentration", domain_level=1),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing", domain_level=1),
    _spell("lesser-restoration", "Lesser Restoration", "healing", "condition-removal", level=2, min_level=3, domain_level=3),
    _spell("spiritual-weapon", "Spiritual Weapon", "damage", "spell-attack", "bonus-action", level=2, min_level=3, domain_level=3),
    _spell("beacon-of-hope", "Beacon of Hope", "buff", "healing-maximize", "saving-throw-advantage", "death-save-advantage", "concentration", level=3, min_level=5, domain_level=5),
    _spell("revivify", "Revivify", "healing", "arena-out-of-scope", level=3, min_level=5, domain_level=5),
    _spell("death-ward", "Death Ward", "healing", "zero-hp-prevention", level=4, min_level=7, domain_level=7),
    _spell("guardian-of-faith", "Guardian of Faith", "damage", "persistent-damage", level=4, min_level=7, domain_level=7),
    _spell("mass-cure-wounds", "Mass Cure Wounds", "healing", "multi-target-healing", level=5, min_level=9, domain_level=9),
    _spell("raise-dead", "Raise Dead", "healing", "arena-out-of-scope", level=5, min_level=9, domain_level=9),
)


def prepared_count_2014(level: int, wisdom_modifier: int) -> int:
    if not 1 <= level <= 20:
        raise ValueError("2014 Cleric level must be between 1 and 20.")
    return max(1, level + wisdom_modifier)


def build_cleric_2014_spell_package(level: int, wisdom_modifier: int) -> ClassSpellPackage:
    try:
        count = prepared_count_2014(level, wisdom_modifier)
        available = [spell for spell in _PREPARED if spell.min_character_level <= level]
        # This initial tranche intentionally defines enough selected spells for levels 1-3.
        # Later levels extend the same ordered package instead of replacing it.
        if count > len(available):
            raise ValueError(
                f"2014 Cleric level {level} needs {count} prepared spells; "
                f"the canonical package currently defines {len(available)} legal choices."
            )
        domain = [
            spell for spell in _DOMAIN
            if spell.always_prepared_from_level is not None
            and level >= spell.always_prepared_from_level
        ]
        return ClassSpellPackage(
            class_id="cleric",
            casting_ability="wisdom",
            cantrips=list(_CANTRIPS),
            spells=available[:count],
            always_prepared_spells=domain,
        )
    except Exception:
        logger.exception("Failed to build 2014 Cleric spell package at level %s", level)
        raise
