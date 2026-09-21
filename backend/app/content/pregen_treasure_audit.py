from __future__ import annotations

from app.domain.combat_treasure import CombatTreasureAward
from app.domain.models import CombatantTemplate


def awards(template: CombatantTemplate) -> list[CombatTreasureAward]:
    return list(template.combat_treasure_awards)


def stat_bonus(template: CombatantTemplate, effect: str, *, multiplier: int = 1) -> int:
    return sum(item.bonus * multiplier for item in awards(template) if item.effect == effect)


def expected_defense_stats(
    template: CombatantTemplate, armor_class: int, max_hp: int, speed_ft: int,
) -> tuple[int, int, int]:
    return (
        armor_class + stat_bonus(template, "armor-class"),
        max_hp + stat_bonus(template, "max-hp", multiplier=5),
        speed_ft + stat_bonus(template, "speed", multiplier=5),
    )


def expected_initiative(template: CombatantTemplate, base: int) -> int:
    return base + stat_bonus(template, "initiative")


def expected_saves(template: CombatantTemplate, base: dict[str, int]) -> dict[str, int]:
    bonus = stat_bonus(template, "saving-throws")
    return {ability: value + bonus for ability, value in base.items()}


def expected_resources(template: CombatantTemplate, base: dict[str, int]) -> dict[str, int]:
    expected = dict(base)
    if any(item.effect == "healing-potion" for item in awards(template)):
        expected["combat-healing-potion"] = 1
    return expected


def weapon_bonus(template: CombatantTemplate, attack_id: str) -> int:
    return sum(
        item.bonus for item in awards(template)
        if item.effect == "weapon-enhancement" and item.target_id == attack_id
    )
