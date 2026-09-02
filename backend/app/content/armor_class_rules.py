from __future__ import annotations

import logging
from typing import Literal

from app.content.fighting_style_rules import FightingStyleSelection, has_fighting_style

logger = logging.getLogger(__name__)
ArmorCategory = Literal["none", "light", "medium", "heavy"]


def defense_fighting_style_bonus(
    fighting_styles: FightingStyleSelection,
    armor_category: ArmorCategory,
) -> int:
    """Return the static 2024 Defense Fighting Style AC bonus for an armored loadout."""
    try:
        if armor_category not in {"none", "light", "medium", "heavy"}:
            raise ValueError(f"Unsupported armor category: {armor_category!r}.")
        return 1 if has_fighting_style(fighting_styles, "Defense") and armor_category != "none" else 0
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Defense Fighting Style AC compilation failed.")
        raise RuntimeError("Defense Fighting Style AC could not be compiled.") from exc


def armor_dexterity_bonus(armor_category: ArmorCategory, dexterity_modifier: int) -> int:
    """Return the Dexterity contribution used by worn armor in the 2024 rules."""
    if armor_category == "light" or armor_category == "none":
        return dexterity_modifier
    if armor_category == "medium":
        return min(dexterity_modifier, 2)
    if armor_category == "heavy":
        return 0
    raise ValueError(f"Unsupported armor category: {armor_category!r}.")


def shield_armor_class_bonus(*, wielding_shield: bool, shield_trained: bool) -> int:
    """Return the static Shield AC bonus; an untrained shield grants no AC bonus."""
    try:
        if not isinstance(wielding_shield, bool) or not isinstance(shield_trained, bool):
            raise ValueError("Shield AC flags must be booleans.")
        return 2 if wielding_shield and shield_trained else 0
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Shield AC compilation failed.")
        raise RuntimeError("Shield AC could not be compiled.") from exc


def compile_armored_base_ac(
    armor_base_ac: int,
    fighting_styles: FightingStyleSelection,
    armor_category: ArmorCategory,
) -> int:
    """Compile permanent armor/style AC before temporary combat modifiers."""
    try:
        if armor_base_ac < 0:
            raise ValueError("Armor base AC cannot be negative.")
        return armor_base_ac + defense_fighting_style_bonus(fighting_styles, armor_category)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Armored base AC compilation failed.")
        raise RuntimeError("Armored base AC could not be compiled.") from exc


def compile_equipped_base_ac(
    armor_base_ac: int,
    fighting_styles: FightingStyleSelection,
    armor_category: ArmorCategory,
    *,
    wielding_shield: bool,
    shield_trained: bool,
) -> int:
    """Compile permanent armor, fighting-style, and shield AC into the template base AC."""
    try:
        return compile_armored_base_ac(
            armor_base_ac,
            fighting_styles,
            armor_category,
        ) + shield_armor_class_bonus(
            wielding_shield=wielding_shield,
            shield_trained=shield_trained,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Equipped base AC compilation failed.")
        raise RuntimeError("Equipped base AC could not be compiled.") from exc


def compile_worn_armor_class(
    armor_base_ac: int,
    armor_category: ArmorCategory,
    dexterity_modifier: int,
    fighting_styles: FightingStyleSelection,
    *,
    wielding_shield: bool = False,
    shield_trained: bool = False,
) -> int:
    """Compile armor formula + styles + shield from character sheet facts."""
    worn_base = armor_base_ac + armor_dexterity_bonus(armor_category, dexterity_modifier)
    return compile_equipped_base_ac(
        worn_base, fighting_styles, armor_category,
        wielding_shield=wielding_shield, shield_trained=shield_trained,
    )
