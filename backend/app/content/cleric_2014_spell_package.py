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
    _spell("thaumaturgy", "Thaumaturgy", "utility", "arena-out-of-scope", level=0),
    _spell("mending", "Mending", "utility", "arena-out-of-scope", level=0, min_level=4),
    _spell("light", "Light", "utility", "arena-out-of-scope", level=0, min_level=10),
)

# Clerics prepare from the class list after each long rest. This deterministic
# combat package may replace lower-priority prepared choices when higher spell
# levels unlock; that is a legal preparation change by the same character.
_PREPARED = (
    # Preserve Seraphine's established low-level package first. At each level the
    # same Cleric may legally reprepare spells; new choices are appended in the
    # deterministic combat-first order rather than rebuilding the character.
    _spell("healing-word", "Healing Word", "healing", "healing", "bonus-action"),
    _spell("guiding-bolt", "Guiding Bolt", "mixed", "spell-attack", "next-attack-advantage"),
    _spell("shield-of-faith", "Shield of Faith", "buff", "modifier-stack", "concentration"),
    _spell("inflict-wounds", "Inflict Wounds", "damage", "spell-attack"),
    _spell("sanctuary", "Sanctuary", "buff", "attack-gate-save", "bonus-action"),
    _spell("aid", "Aid", "healing", "max-hp-increase", level=2, min_level=3),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("augury", "Augury", "utility", "arena-out-of-scope", level=2, min_level=3),
    _spell("prayer-of-healing", "Prayer of Healing", "healing", "arena-out-of-scope", level=2, min_level=3),
    _spell("warding-bond", "Warding Bond", "buff", "damage-resistance", level=2, min_level=3),
    _spell("hold-person", "Hold Person", "control", "condition", "repeat-save", level=2, min_level=3),
    _spell("silence", "Silence", "control", "area-effect", "concentration", level=2, min_level=3),
    _spell("mass-healing-word", "Mass Healing Word", "healing", "multi-target-healing", "bonus-action", level=3, min_level=5),
    _spell("spirit-guardians", "Spirit Guardians", "damage", "persistent-damage", "concentration", level=3, min_level=5),
    _spell("dispel-magic", "Dispel Magic", "control", "effect-removal", level=3, min_level=5),
    _spell("protection-from-energy", "Protection from Energy", "buff", "damage-resistance", "concentration", level=3, min_level=5),
    _spell("remove-curse", "Remove Curse", "healing", "effect-removal", level=3, min_level=5),
    _spell("freedom-of-movement", "Freedom of Movement", "buff", "condition-prevention", level=4, min_level=7),
    _spell("locate-creature", "Locate Creature", "utility", "arena-out-of-scope", level=4, min_level=7),
    _spell("flame-strike", "Flame Strike", "damage", "save-damage", "area-effect", level=5, min_level=9),
    _spell("greater-restoration", "Greater Restoration", "healing", "condition-removal", level=5, min_level=9),
    _spell("commune", "Commune", "utility", "arena-out-of-scope", level=5, min_level=9),
    _spell("harm", "Harm", "damage", "save-damage", level=6, min_level=11),
    _spell("heal", "Heal", "healing", "healing", level=6, min_level=11),
    _spell("blade-barrier", "Blade Barrier", "damage", "area-effect", "concentration", level=6, min_level=11),
    _spell("fire-storm", "Fire Storm", "damage", "save-damage", "area-effect", level=7, min_level=13),
    _spell("regenerate", "Regenerate", "healing", "healing", level=7, min_level=13),
    _spell("earthquake", "Earthquake", "damage", "area-effect", "concentration", level=8, min_level=15),
    _spell("holy-aura", "Holy Aura", "buff", "modifier-stack", "concentration", level=8, min_level=15),
    _spell("mass-heal", "Mass Heal", "healing", "multi-target-healing", level=9, min_level=17),
    _spell("gate", "Gate", "utility", "arena-out-of-scope", level=9, min_level=17),
)

_DOMAIN = (
    _spell("bless", "Bless", "buff", "modifier-stack", "concentration", domain_level=1),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing", domain_level=1),
    _spell("lesser-restoration", "Lesser Restoration", "healing", "condition-removal", level=2, min_level=3, domain_level=3),
    _spell("spiritual-weapon", "Spiritual Weapon", "damage", "persistent-spell-attack", "bonus-action", level=2, min_level=3, domain_level=3),
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
            cantrips=[
                spell for spell in _CANTRIPS
                if spell.min_character_level <= level
            ],
            spells=available[:count],
            always_prepared_spells=domain,
        )
    except Exception:
        logger.exception("Failed to build 2014 Cleric spell package at level %s", level)
        raise
