from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost, ConditionName
from app.domain.grid import GridPosition
from app.domain.save_damage import DamageTypeName

logger = logging.getLogger(__name__)

SaveZoneTrigger = Literal["appear", "start_turn", "enter", "end_turn"]


class PersistentSaveZoneAction(BaseModel):
    """Placed sphere that forces a save at printed appear/start/enter/end windows."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    cast_range_ft: int = Field(ge=0)
    radius_ft: int = Field(ge=5)
    duration_rounds: int = Field(ge=1)
    concentration: bool = False
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    triggers: list[SaveZoneTrigger] = Field(min_length=1)
    save_triggers: list[SaveZoneTrigger] = Field(default_factory=list)
    once_per_turn: bool = True
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=8, ge=2, le=100)
    damage_type: DamageTypeName | None = None
    success_damage: Literal["none", "half"] = "none"
    upcast_dice_per_level: int = Field(default=0, ge=0, le=20)
    failed_save_condition_id: ConditionName | None = None
    failed_save_duration_rounds: int = Field(default=1, ge=1, le=20)
    failed_save_suppress_action: bool = False
    failed_save_suppress_bonus_action: bool = False
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    expends_spell_slot: bool = False
    animation: str = "save-zone"
    source: str | None = None

    @model_validator(mode="after")
    def validate_zone(self) -> "PersistentSaveZoneAction":
        try:
            if self.radius_ft % 5:
                raise ValueError("Save zones must use 5-foot increments.")
            if len(set(self.triggers)) != len(self.triggers):
                raise ValueError("Save-zone triggers must be unique.")
            if self.save_triggers and (
                len(set(self.save_triggers)) != len(self.save_triggers)
                or not set(self.save_triggers).issubset(self.triggers)
            ):
                raise ValueError("Save-zone save triggers must be unique and listed in triggers.")
            if self.damage_dice_count and self.damage_type is None:
                raise ValueError("Damaging save zones require a damage type.")
            if not self.damage_dice_count and self.failed_save_condition_id is None:
                raise ValueError("Save zones require damage or a failed-save condition.")
            slot_resource = bool(self.resource_id and self.resource_id.startswith("spell-slot-"))
            if slot_resource != self.expends_spell_slot:
                raise ValueError("Save-zone spell-slot resource and expends_spell_slot must agree.")
            return self
        except Exception:
            logger.exception("Save-zone schema validation failed for %s.", self.id)
            raise


class PersistentSaveZoneState(BaseModel):
    """Mutable per-fight placement for one save zone."""

    zone_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_side: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    position: GridPosition
    radius_ft: int = Field(ge=5)
    expires_round: int = Field(ge=1)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    triggers: list[SaveZoneTrigger] = Field(min_length=1)
    save_triggers: list[SaveZoneTrigger] = Field(default_factory=list)
    once_per_turn: bool = True
    damage_dice_count: int = Field(default=0, ge=0)
    damage_dice_size: int = Field(default=8, ge=2)
    damage_type: DamageTypeName | None = None
    success_damage: Literal["none", "half"] = "none"
    failed_save_condition_id: ConditionName | None = None
    failed_save_duration_rounds: int = 1
    failed_save_suppress_action: bool = False
    failed_save_suppress_bonus_action: bool = False
    concentration: bool = False
    triggered_turn_keys: dict[str, str] = Field(default_factory=dict)
    animation: str = "save-zone"
