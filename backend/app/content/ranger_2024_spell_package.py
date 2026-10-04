from __future__ import annotations

import logging

from app.content.canonical_spell_choice import spell_choice as _spell
from app.content.class_spell_progression import prepared_spell_count
from app.content.ranger_combat_levels import RANGER_COMBAT_LEVELS
from app.domain.class_loadouts import ClassSpellPackage

logger = logging.getLogger(__name__)


def _ordinary(level: int):
    spells = []
    if level >= 17:
        spells.append(_spell(
            "commune-with-nature", "Commune with Nature", "utility", "arena-out-of-scope",
            spell_level=5, min_character_level=17,
        ))
    if level >= 13:
        spells.append(_spell(
            "freedom-of-movement", "Freedom of Movement", "buff", "debuff-counter",
            spell_level=4, min_character_level=13,
        ))
    if level >= 9:
        spells.extend([
            _spell(
                "dispel-magic", "Dispel Magic", "control", "effect-removal",
                spell_level=3, min_character_level=9,
            ),
            _spell(
                "daylight", "Daylight", "utility", "arena-out-of-scope",
                spell_level=3, min_character_level=9,
            ),
        ])
    if level >= 5:
        spells.extend([
            _spell(
                "lesser-restoration", "Lesser Restoration", "healing", "condition-removal",
                spell_level=2, min_character_level=5,
            ),
            _spell(
                "aid", "Aid", "buff", "modifier-stack",
                spell_level=2, min_character_level=5,
            ),
            _spell(
                "barkskin", "Barkskin", "buff", "modifier-stack",
                spell_level=2, min_character_level=5,
            ),
        ])
    spells.extend([
        _spell("ensnaring-strike", "Ensnaring Strike", "damage", "post-hit-save-condition", "restrained", "concentration"),
        _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
        _spell("longstrider", "Longstrider", "buff", "modifier-stack"),
        _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
        _spell("speak-with-animals", "Speak with Animals", "utility", "arena-out-of-scope"),
        _spell("alarm", "Alarm", "utility", "arena-out-of-scope"),
        _spell(
            "locate-object", "Locate Object", "utility", "arena-out-of-scope",
            spell_level=2, min_character_level=5,
        ),
        _spell(
            "water-walk", "Water Walk", "utility", "arena-out-of-scope",
            spell_level=3, min_character_level=9,
        ),
    ])
    return spells


def build_ranger_2024_spell_package(level: int) -> ClassSpellPackage:
    try:
        if level not in RANGER_COMBAT_LEVELS:
            raise ValueError("2024 Ranger spellcasting covers levels 1 through 20.")
        expected = prepared_spell_count("ranger", level)
        ordinary = [spell for spell in _ordinary(level) if spell.min_character_level <= level]
        if len(ordinary) < expected:
            raise ValueError(
                f"ranger level {level} canonical package is incomplete: "
                f"needs {expected} prepared spells, has {len(ordinary)}."
            )
        return ClassSpellPackage(
            class_id="ranger",
            casting_ability="wisdom",
            cantrips=[],
            spells=ordinary[:expected],
            always_prepared_spells=[
                _spell(
                    "hunters-mark", "Hunter's Mark", "damage",
                    "targeted-concentration-damage", "concentration",
                    always_prepared_from_level=1,
                ),
            ],
        )
    except Exception:
        logger.exception("Failed to build 2024 Ranger spell package at level %s.", level)
        raise
