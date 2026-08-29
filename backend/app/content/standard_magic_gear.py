from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MagicItemBudget:
    common: int
    uncommon: int
    rare: int
    very_rare: int


@dataclass(frozen=True)
class MartialEnhancementProfile:
    weapon_bonus: int
    armor_bonus: int
    shield_bonus: int
    utility_items: int


def higher_level_magic_item_budget(level: int) -> MagicItemBudget:
    """2024 higher-level starting-character magic-item guidance."""
    if not 1 <= level <= 20:
        raise ValueError("Character level must be 1-20.")
    if level == 1:
        return MagicItemBudget(0, 0, 0, 0)
    if level <= 4:
        return MagicItemBudget(1, 0, 0, 0)
    if level <= 10:
        return MagicItemBudget(1, 1, 0, 0)
    if level <= 16:
        return MagicItemBudget(2, 3, 1, 0)
    return MagicItemBudget(2, 4, 3, 1)


def standard_martial_enhancements(level: int, *, uses_shield: bool) -> MartialEnhancementProfile:
    """Simple Iron Pit standard loadout kept within the 2024 rarity budget."""
    higher_level_magic_item_budget(level)
    if level <= 4:
        return MartialEnhancementProfile(0, 0, 0, 0)
    if level <= 10:
        return MartialEnhancementProfile(1, 0, 0, 1)
    if level <= 16:
        return MartialEnhancementProfile(2, 0, 1 if uses_shield else 0, 1)
    return MartialEnhancementProfile(3, 1, 1 if uses_shield else 0, 2)
