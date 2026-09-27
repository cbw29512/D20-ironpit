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
    _spell("fire-bolt", "Fire Bolt", "damage", "spell-attack", "cantrip-scaling", level=0),
    _spell("poison-spray", "Poison Spray", "damage", "save-damage", "cantrip-scaling", level=0),
    _spell("ray-of-frost", "Ray of Frost", "mixed", "spell-attack", "speed", "cantrip-scaling", level=0),
    _spell("shocking-grasp", "Shocking Grasp", "damage", "spell-attack", "cantrip-scaling", level=0, min_level=4),
    _spell("light", "Light", "utility", "arena-out-of-scope", level=0, min_level=10),
)

_PREPARED = (
    _spell("magic-missile", "Magic Missile", "damage", "auto-hit-spell"),
    _spell("burning-hands", "Burning Hands", "damage", "save-damage", "area-effect"),
    _spell("false-life", "False Life", "buff", "temporary-hp"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("identify", "Identify", "utility", "arena-out-of-scope", min_level=2),
    _spell("shatter", "Shatter", "damage", "save-damage", "area-effect", level=2, min_level=3),
    _spell("comprehend-languages", "Comprehend Languages", "utility", "arena-out-of-scope", min_level=4),
    _spell("locate-object", "Locate Object", "utility", "arena-out-of-scope", level=2, min_level=4),
    _spell("fireball", "Fireball", "damage", "save-damage", "area-effect", level=3, min_level=5),
    _spell("dispel-magic", "Dispel Magic", "control", "effect-removal", level=3, min_level=6),
    _spell("greater-invisibility", "Greater Invisibility", "buff", "condition", "concentration", level=4, min_level=7),
    _spell("arcane-eye", "Arcane Eye", "utility", "arena-out-of-scope", level=4, min_level=8),
    _spell("hallucinatory-terrain", "Hallucinatory Terrain", "utility", "arena-out-of-scope", level=4, min_level=8),
    _spell("cone-of-cold", "Cone of Cold", "damage", "save-damage", "area-effect", level=5, min_level=9),
    _spell("creation", "Creation", "utility", "arena-out-of-scope", level=5, min_level=10),
    _spell("circle-of-death", "Circle of Death", "damage", "save-damage", "area-effect", level=6, min_level=11),
    _spell("telepathic-bond", "Rary's Telepathic Bond", "utility", "arena-out-of-scope", level=5, min_level=12),
    _spell("finger-of-death", "Finger of Death", "damage", "save-damage", level=7, min_level=13),
    _spell("scrying", "Scrying", "utility", "arena-out-of-scope", level=5, min_level=14),
    _spell("power-word-stun", "Power Word Stun", "control", "hp-threshold-condition", level=8, min_level=15),
    _spell("contact-other-plane", "Contact Other Plane", "utility", "arena-out-of-scope", level=5, min_level=16),
    _spell("power-word-kill", "Power Word Kill", "damage", "hp-threshold-instant-death", level=9, min_level=17),
    _spell("unseen-servant", "Unseen Servant", "utility", "arena-out-of-scope", min_level=18),
    _spell("magic-mouth", "Magic Mouth", "utility", "arena-out-of-scope", level=2, min_level=19),
    _spell("tongues", "Tongues", "utility", "arena-out-of-scope", level=3, min_level=20),
)


def prepared_count_2014(level: int, intelligence_modifier: int) -> int:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Wizard level must be between 1 and 20.")
        return max(1, level + intelligence_modifier)
    except Exception:
        logger.exception("Failed to compute 2014 Wizard prepared-spell count at level %s.", level)
        raise


def build_wizard_2014_spell_package(level: int, intelligence_modifier: int) -> ClassSpellPackage:
    try:
        from app.content.wizard_2014_progression import wizard_2014_level

        row = wizard_2014_level(level)
        count = prepared_count_2014(level, intelligence_modifier)
        available = [spell for spell in _PREPARED if spell.min_character_level <= level]
        if count > len(available):
            raise ValueError(
                f"2014 Wizard level {level} needs {count} prepared spells; "
                f"the canonical package currently defines {len(available)} legal choices."
            )
        cantrips = [spell for spell in _CANTRIPS if spell.min_character_level <= level]
        if len(cantrips) != row.cantrips_known:
            raise ValueError(
                f"2014 Wizard level {level} needs {row.cantrips_known} cantrips; "
                f"the canonical package defines {len(cantrips)}."
            )
        return ClassSpellPackage(
            class_id="wizard",
            casting_ability="intelligence",
            cantrips=cantrips,
            spells=available[:count],
        )
    except Exception:
        logger.exception("Failed to build 2014 Wizard spell package at level %s.", level)
        raise
