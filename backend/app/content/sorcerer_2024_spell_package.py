from __future__ import annotations

import logging

from app.content.canonical_spell_choice import spell_choice as _spell
from app.content.class_spell_progression import prepared_spell_count
from app.content.sorcerer_combat_levels import SORCERER_COMBAT_LEVELS
from app.domain.class_loadouts import ClassSpellPackage

logger = logging.getLogger(__name__)


def _cantrips(level: int):
    cantrips = [
        _spell("fire-bolt", "Fire Bolt", "damage", "spell-attack", spell_level=0),
        _spell("poison-spray", "Poison Spray", "damage", "spell-attack", "cantrip-scaling", spell_level=0),
        _spell("prestidigitation", "Prestidigitation", "utility", "arena-out-of-scope", spell_level=0),
        _spell("light", "Light", "utility", "arena-out-of-scope", spell_level=0),
    ]
    if level >= 4:
        cantrips.append(
            _spell("thunderclap", "Thunderclap", "damage", "save-damage", "area",
                   spell_level=0, min_character_level=4)
        )
    if level >= 10:
        cantrips.append(
            _spell("mage-hand", "Mage Hand", "utility", "arena-out-of-scope",
                   spell_level=0, min_character_level=10)
        )
    return cantrips


def _ordinary(level: int):
    spells = [
        _spell("burning-hands", "Burning Hands", "damage", "save-damage", "area"),
        _spell("magic-missile", "Magic Missile", "damage", "auto-hit-projectiles"),
        _spell("thunderwave", "Thunderwave", "damage", "save-damage", "forced-movement"),
        _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    ]
    if level >= 3:
        spells.append(_spell(
            "shatter", "Shatter", "damage", "save-damage", "area",
            spell_level=2, min_character_level=3,
        ))
        spells.append(_spell(
            "comprehend-languages", "Comprehend Languages", "utility", "arena-out-of-scope",
            min_character_level=3,
        ))
    if level >= 4:
        spells.append(_spell(
            "identify", "Identify", "utility", "arena-out-of-scope", min_character_level=4,
        ))
    if level >= 5:
        spells.extend([
            _spell("fireball", "Fireball", "damage", "save-damage", "area",
                   spell_level=3, min_character_level=5),
            _spell("knock", "Knock", "utility", "arena-out-of-scope",
                   spell_level=2, min_character_level=5),
        ])
    if level >= 6:
        spells.append(_spell(
            "lightning-bolt", "Lightning Bolt", "damage", "save-damage", "area",
            spell_level=3, min_character_level=6,
        ))
    if level >= 7:
        spells.append(_spell(
            "blight", "Blight", "damage", "save-damage",
            spell_level=4, min_character_level=7,
        ))
    if level >= 8:
        spells.append(_spell(
            "greater-invisibility", "Greater Invisibility", "buff",
            "condition", "concentration", spell_level=4, min_character_level=8,
        ))
    if level >= 9:
        spells.extend([
            _spell("cone-of-cold", "Cone of Cold", "damage", "save-damage", "area",
                   spell_level=5, min_character_level=9),
            _spell("dispel-magic", "Dispel Magic", "control", "effect-removal",
                   spell_level=3, min_character_level=9),
        ])
    if level >= 10:
        spells.append(_spell(
            "creation", "Creation", "utility", "arena-out-of-scope",
            spell_level=5, min_character_level=10,
        ))
    if level >= 11:
        spells.append(_spell(
            "disintegrate", "Disintegrate", "damage", "save-damage",
            spell_level=6, min_character_level=11,
        ))
    if level >= 13:
        spells.append(_spell(
            "finger-of-death", "Finger of Death", "damage", "save-damage",
            spell_level=7, min_character_level=13,
        ))
    if level >= 15:
        spells.append(_spell(
            "sunburst", "Sunburst", "damage", "save-damage", "area",
            spell_level=8, min_character_level=15,
        ))
    if level >= 17:
        spells.append(_spell(
            "circle-of-death", "Circle of Death", "damage", "save-damage", "area",
            spell_level=6, min_character_level=17,
        ))
    if level >= 18:
        spells.append(_spell(
            "tongues", "Tongues", "utility", "arena-out-of-scope",
            spell_level=3, min_character_level=18,
        ))
    if level >= 19:
        spells.append(_spell(
            "water-breathing", "Water Breathing", "utility", "arena-out-of-scope",
            spell_level=3, min_character_level=19,
        ))
    if level >= 20:
        spells.append(_spell(
            "illusory-script", "Illusory Script", "utility", "arena-out-of-scope",
            min_character_level=20,
        ))
    return spells


def _always_prepared(level: int):
    always = []
    if level >= 3:
        always.extend([
            _spell("alter-self", "Alter Self", "utility", "arena-out-of-scope",
                   spell_level=2, min_character_level=3, always_prepared_from_level=3),
            _spell("chromatic-orb", "Chromatic Orb", "damage", "spell-attack",
                   always_prepared_from_level=3),
            _spell("command", "Command", "control", "arena-out-of-scope",
                   always_prepared_from_level=3),
            _spell("dragons-breath", "Dragon's Breath", "damage", "save-damage", "concentration",
                   spell_level=2, min_character_level=3, always_prepared_from_level=3),
        ])
    if level >= 5:
        always.extend([
            _spell("fear", "Fear", "control", "arena-out-of-scope",
                   spell_level=3, min_character_level=5, always_prepared_from_level=5),
            _spell("fly", "Fly", "utility", "arena-out-of-scope",
                   spell_level=3, min_character_level=5, always_prepared_from_level=5),
        ])
    if level >= 7:
        always.extend([
            _spell("arcane-eye", "Arcane Eye", "utility", "arena-out-of-scope",
                   spell_level=4, min_character_level=7, always_prepared_from_level=7),
            _spell("charm-monster", "Charm Monster", "control", "arena-out-of-scope",
                   spell_level=4, min_character_level=7, always_prepared_from_level=7),
        ])
    if level >= 9:
        always.extend([
            _spell("legend-lore", "Legend Lore", "utility", "arena-out-of-scope",
                   spell_level=5, min_character_level=9, always_prepared_from_level=9),
            _spell("summon-dragon", "Summon Dragon", "utility", "arena-unavailable-summon",
                   spell_level=5, min_character_level=9, always_prepared_from_level=9),
        ])
    return always


def build_sorcerer_2024_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Sorcerer canonical spell package currently certifies levels 1 through 20.")
        expected = prepared_spell_count("sorcerer", level)
        expected_cantrips = SORCERER_COMBAT_LEVELS[level].cantrips
        cantrips = _cantrips(level)
        ordinary = _ordinary(level)
        if len(ordinary) < expected:
            raise ValueError(
                f"sorcerer level {level} canonical package is incomplete: "
                f"needs {expected} prepared spells, has {len(ordinary)}."
            )
        if len(cantrips) != expected_cantrips:
            raise ValueError(
                f"sorcerer level {level} canonical package needs {expected_cantrips} cantrips, "
                f"has {len(cantrips)}."
            )
        return ClassSpellPackage(
            class_id="sorcerer",
            casting_ability="charisma",
            cantrips=cantrips,
            spells=ordinary[:expected],
            always_prepared_spells=_always_prepared(level),
        )
    except Exception:
        logger.exception("Failed to build 2024 Sorcerer spell package at level %s.", level)
        raise
