from __future__ import annotations

import logging

from app.content.canonical_spell_choice import spell_choice as _spell
from app.content.class_spell_progression import prepared_spell_count
from app.content.warlock_combat_levels import WARLOCK_COMBAT_LEVELS
from app.domain.class_loadouts import ClassSpellPackage

logger = logging.getLogger(__name__)


def _cantrips(level: int):
    cantrips = [
        _spell("eldritch-blast", "Eldritch Blast", "damage", "spell-attack", spell_level=0),
        _spell(
            "prestidigitation", "Prestidigitation", "utility", "arena-out-of-scope",
            spell_level=0,
        ),
    ]
    if level >= 4:
        cantrips.append(
            _spell("mage-hand", "Mage Hand", "utility", "arena-out-of-scope", spell_level=0, min_character_level=4)
        )
    if level >= 10:
        cantrips.append(
            _spell(
                "poison-spray", "Poison Spray", "damage", "spell-attack", "cantrip-scaling",
                spell_level=0, min_character_level=10,
            )
        )
    return cantrips


def _ordinary(level: int):
    spells = [
        _spell("hex", "Hex", "mixed", "targeted-concentration-damage", "concentration"),
        _spell("charm-person", "Charm Person", "control", "charmed"),
    ]
    if level >= 2:
        spells.append(_spell(
            "comprehend-languages", "Comprehend Languages", "utility", "arena-out-of-scope",
            min_character_level=2,
        ))
    if level >= 3:
        spells.append(_spell(
            "detect-magic", "Detect Magic", "utility", "arena-out-of-scope",
            min_character_level=3,
        ))
    if level >= 4:
        spells.append(_spell(
            "protection-from-evil-and-good", "Protection from Evil and Good", "utility",
            "arena-out-of-scope", min_character_level=4,
        ))
    if level >= 5:
        spells.append(_spell(
            "hold-person", "Hold Person", "control", "paralyzed", "concentration",
            spell_level=2, min_character_level=5,
        ))
    if level >= 6:
        spells.append(_spell(
            "dispel-magic", "Dispel Magic", "control", "effect-removal",
            spell_level=3, min_character_level=6,
        ))
    if level >= 7:
        spells.append(_spell("blight", "Blight", "damage", "save-damage", spell_level=4, min_character_level=7))
    if level >= 8:
        spells.append(_spell(
            "dimension-door", "Dimension Door", "utility", "teleport",
            spell_level=4, min_character_level=8,
        ))
    if level >= 9:
        spells.append(_spell("dream", "Dream", "utility", "arena-out-of-scope", spell_level=5, min_character_level=9))
    if level >= 11:
        spells.append(_spell("scrying", "Scrying", "utility", "arena-out-of-scope", spell_level=5, min_character_level=11))
    if level >= 13:
        spells.append(_spell(
            "illusory-script", "Illusory Script", "utility", "arena-out-of-scope",
            min_character_level=13,
        ))
    if level >= 15:
        spells.append(_spell("tongues", "Tongues", "utility", "arena-out-of-scope", spell_level=3, min_character_level=15))
    if level >= 17:
        spells.append(_spell(
            "hallucinatory-terrain", "Hallucinatory Terrain", "utility", "arena-out-of-scope",
            spell_level=4, min_character_level=17,
        ))
    if level >= 19:
        spells.append(_spell(
            "invisibility", "Invisibility", "utility", "arena-out-of-scope",
            spell_level=2, min_character_level=19,
        ))
    return spells


def _always_prepared(level: int):
    always = []
    if level >= 3:
        always.extend([
            _spell(
                "burning-hands", "Burning Hands", "damage", "save-damage", "area",
                always_prepared_from_level=3,
            ),
            _spell(
                "command", "Command", "control", "arena-out-of-scope",
                always_prepared_from_level=3,
            ),
            _spell(
                "scorching-ray", "Scorching Ray", "damage", "spell-attack", "multi-attack",
                spell_level=2, min_character_level=3, always_prepared_from_level=3,
            ),
            _spell(
                "suggestion", "Suggestion", "control", "charmed", "concentration",
                spell_level=2, min_character_level=3, always_prepared_from_level=3,
            ),
        ])
    if level >= 5:
        always.extend([
            _spell(
                "fireball", "Fireball", "damage", "save-damage", "area",
                spell_level=3, min_character_level=5, always_prepared_from_level=5,
            ),
            _spell(
                "stinking-cloud", "Stinking Cloud", "control", "arena-out-of-scope",
                spell_level=3, min_character_level=5, always_prepared_from_level=5,
            ),
        ])
    if level >= 7:
        always.extend([
            _spell(
                "fire-shield", "Fire Shield", "buff", "arena-out-of-scope",
                spell_level=4, min_character_level=7, always_prepared_from_level=7,
            ),
            _spell(
                "wall-of-fire", "Wall of Fire", "damage", "arena-out-of-scope",
                spell_level=4, min_character_level=7, always_prepared_from_level=7,
            ),
        ])
    if level >= 9:
        always.extend([
            _spell(
                "contact-other-plane", "Contact Other Plane", "utility", "arena-out-of-scope",
                spell_level=5, min_character_level=9, always_prepared_from_level=9,
            ),
            _spell(
                "geas", "Geas", "control", "arena-out-of-scope",
                spell_level=5, min_character_level=9, always_prepared_from_level=9,
            ),
            _spell(
                "insect-plague", "Insect Plague", "damage", "arena-out-of-scope",
                spell_level=5, min_character_level=9, always_prepared_from_level=9,
            ),
        ])
    return always


def build_warlock_2024_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Warlock canonical spell package currently certifies levels 1 through 20.")
        expected = prepared_spell_count("warlock", level)
        expected_cantrips = WARLOCK_COMBAT_LEVELS[level].cantrips
        cantrips = _cantrips(level)
        ordinary = _ordinary(level)
        if len(ordinary) < expected:
            raise ValueError(
                f"warlock level {level} canonical package is incomplete: "
                f"needs {expected} prepared spells, has {len(ordinary)}."
            )
        if len(cantrips) != expected_cantrips:
            raise ValueError(
                f"warlock level {level} canonical package needs {expected_cantrips} cantrips, "
                f"has {len(cantrips)}."
            )
        return ClassSpellPackage(
            class_id="warlock",
            casting_ability="charisma",
            cantrips=cantrips,
            spells=ordinary[:expected],
            always_prepared_spells=_always_prepared(level),
        )
    except Exception:
        logger.exception("Failed to build 2024 Warlock spell package at level %s.", level)
        raise
