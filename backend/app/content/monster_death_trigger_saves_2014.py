"""Source-validated, source-neutral 2014 death-trigger save bindings.

The trigger owns timing; the shared SavingThrowAction owns the save and typed damage.
These definitions remain blocked until the death-event dispatcher is wired.
"""
from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.content.capability_compiler import _compile_save
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.actions import SavingThrowAction
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.targeting import AreaTargeting
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_REQUIRED = frozenset({
    "id", "name", "save_ability", "dc", "range_ft", "area", "animation",
    "damage_dice_count", "damage_dice_size", "damage_bonus", "damage_type",
    "success_damage",
})


class DeathTriggeredSave(BaseModel):
    """Passive source-death event wrapping a universal save operation."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    trigger: Literal["source_death"] = "source_death"
    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    save_action: SavingThrowAction


def death_trigger_saves_2014(monster: SourceMonster2014) -> list[DeathTriggeredSave]:
    """Compile exact source-declared death saves, never infer from printed names."""
    try:
        compiled: list[DeathTriggeredSave] = []
        seen: set[str] = set()
        for raw in monster.death_trigger_actions:
            if not isinstance(raw, dict) or set(raw) != _REQUIRED:
                raise ValueError(f"{monster.id}: invalid death-trigger source fields.")
            if any(type(raw[key]) is not int for key in (
                "dc", "range_ft", "damage_dice_count", "damage_dice_size", "damage_bonus"
            )):
                raise ValueError(f"{monster.id}: death-trigger numeric fields must be integers.")
            source_name = raw["name"]
            if not isinstance(source_name, str) or source_name not in monster.trait_names:
                raise ValueError(f"{monster.id}: death trigger lacks a matching printed trait.")
            source_key = raw["id"]
            if not isinstance(source_key, str) or not source_key or source_key in seen:
                raise ValueError(f"{monster.id}: duplicate or empty death-trigger id.")
            seen.add(source_key)
            area = AreaTargeting.model_validate(raw["area"])
            if area.shape != "emanation" or area.origin != "self" or area.radius_ft != raw["range_ft"]:
                raise ValueError(f"{monster.id}: death trigger requires matching self-emanation range.")
            card = SaveCapabilityDefinition(
                id=f"2014-{monster.id}-{source_key}",
                name=source_name,
                save_ability=raw["save_ability"],
                dc=raw["dc"],
                range_ft=raw["range_ft"],
                area=area,
                damage=DiceSpec(
                    count=raw["damage_dice_count"],
                    size=raw["damage_dice_size"],
                    bonus=raw["damage_bonus"],
                ),
                damage_type=DamageType(raw["damage_type"]),
                success_damage=raw["success_damage"],
                animation=raw["animation"],
            )
            compiled.append(DeathTriggeredSave(
                source_id=card.id, source_name=source_name, save_action=_compile_save(card),
            ))
        return compiled
    except Exception:
        logger.exception("Failed 2014 death-trigger source binding for %s.", monster.id)
        raise
