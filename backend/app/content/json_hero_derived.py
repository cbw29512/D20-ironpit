from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_unarmored_defense_ac, compile_worn_armor_class
from app.content.character_math import fixed_hit_points
from app.content.fighting_style_rules import FightingStyleSelection

LOGGER = logging.getLogger(__name__)
UNARMORED_ARMOR_IDS = {None, "", "none", "unarmored"}


def ability_modifier(score: int) -> int:
    try:
        return (int(score) - 10) // 2
    except Exception:
        LOGGER.exception("Unable to derive ability modifier score=%s", score)
        raise


def derive_hit_points(level: int, hit_die: int, constitution_score: int) -> int:
    """RAW 2014/2024: current Constitution modifier is treated as if it applied from level 1."""
    try:
        return fixed_hit_points(level, hit_die, ability_modifier(constitution_score))
    except Exception:
        LOGGER.exception(
            "Unable to derive hit points level=%s hit_die=%s constitution=%s",
            level, hit_die, constitution_score,
        )
        raise


def derive_armor_class(
    armor_id: str | None,
    ability_scores: dict[str, int],
    fighting_styles: FightingStyleSelection,
    *,
    wielding_shield: bool,
    unarmored_defense_abilities: list[str],
    unarmored_defense_allows_shield: bool,
    shield_trained: bool = True,
) -> int:
    """Derive AC from worn armor or Unarmored Defense. Names are not consulted."""
    try:
        dexterity = ability_modifier(int(ability_scores["dexterity"]))
        if armor_id not in UNARMORED_ARMOR_IDS:
            armor = get_armor(str(armor_id))
            return compile_worn_armor_class(
                armor.base_ac,
                armor.category,
                dexterity,
                fighting_styles,
                wielding_shield=wielding_shield,
                shield_trained=shield_trained,
            )
        if unarmored_defense_abilities:
            modifiers = [
                ability_modifier(int(ability_scores[ability]))
                for ability in unarmored_defense_abilities
            ]
            return compile_unarmored_defense_ac(
                modifiers,
                wielding_shield=wielding_shield,
                allows_shield=unarmored_defense_allows_shield,
            )
        return 10 + dexterity + (2 if wielding_shield and shield_trained else 0)
    except Exception:
        LOGGER.exception(
            "Unable to derive armor class armor=%s shield=%s styles=%s",
            armor_id, wielding_shield, fighting_styles,
        )
        raise


def require_matching_fingerprint(label: str, derived: int, expected: int | None) -> int:
    try:
        if expected is not None and derived != expected:
            raise ValueError(
                f"{label} derived {derived} does not match canonical fingerprint {expected}."
            )
        return derived
    except ValueError:
        LOGGER.exception(
            "Derived-stat fingerprint mismatch label=%s derived=%s expected=%s",
            label, derived, expected,
        )
        raise
    except Exception:
        LOGGER.exception("Fingerprint check failed label=%s", label)
        raise
