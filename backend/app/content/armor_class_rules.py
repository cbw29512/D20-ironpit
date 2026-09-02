from __future__ import annotations

import logging
from typing import Literal

logger = logging.getLogger(__name__)
ArmorCategory = Literal["none", "light", "medium", "heavy"]


def defense_fighting_style_bonus(
    fighting_style: str | None,
    armor_category: ArmorCategory,
) -> int:
    """Return the static 2024 Defense Fighting Style AC bonus for an armored loadout."""
    try:
        if armor_category not in {"none", "light", "medium", "heavy"}:
            raise ValueError(f"Unsupported armor category: {armor_category!r}.")
        return 1 if fighting_style == "Defense" and armor_category != "none" else 0
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Defense Fighting Style AC compilation failed.")
        raise RuntimeError("Defense Fighting Style AC could not be compiled.") from exc


def compile_armored_base_ac(
    armor_base_ac: int,
    fighting_style: str | None,
    armor_category: ArmorCategory,
) -> int:
    """Compile permanent equipment/style AC before temporary combat modifiers."""
    try:
        if armor_base_ac < 0:
            raise ValueError("Armor base AC cannot be negative.")
        return armor_base_ac + defense_fighting_style_bonus(fighting_style, armor_category)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Armored base AC compilation failed.")
        raise RuntimeError("Armored base AC could not be compiled.") from exc
