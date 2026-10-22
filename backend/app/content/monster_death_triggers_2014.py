"""Compile immutable 2014 source death actions into shared save capabilities."""
from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.capabilities import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec


def _compile(raw: object) -> SaveCapabilityDefinition:
    if not isinstance(raw, dict):
        raise ValueError("Death Trigger action must be a structured source declaration.")
    required = {
        "id", "name", "save_ability", "dc", "range_ft", "damage_dice_count",
        "damage_dice_size", "damage_bonus", "damage_type", "success_damage", "area",
    }
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"Death Trigger action is missing fields: {', '.join(missing)}")
    expected_area = {
        "shape": "emanation", "origin": "self", "radius_ft": raw["range_ft"],
    }
    if raw["area"] != expected_area:
        raise ValueError(f"Unsupported Death Trigger geometry: {raw!r}")
    return SaveCapabilityDefinition(
        id=str(raw["id"]),
        name=str(raw["name"]),
        save_ability=raw["save_ability"],
        dc=raw["dc"],
        range_ft=raw["range_ft"],
        max_targets=20,
        target_scope="all-other-creatures",
        area=raw["area"],
        damage=DiceSpec(
            count=raw["damage_dice_count"],
            size=raw["damage_dice_size"],
            bonus=raw["damage_bonus"],
        ),
        damage_type=raw["damage_type"],
        success_damage=raw["success_damage"],
        animation=raw.get("animation", "death-trigger"),
    )


def death_trigger_actions_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    return [_compile(raw) for raw in monster.death_trigger_actions]


def supports_death_triggers_2014(monster: SourceMonster2014) -> bool:
    if not monster.death_trigger_actions:
        return True
    try:
        actions = death_trigger_actions_2014(monster)
        return len({action.id for action in actions}) == len(actions)
    except (KeyError, TypeError, ValueError):
        return False
