from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.save_damage import DamageTypeName

ActionCost = Literal["action", "bonus_action", "reaction"]


class HpThresholdInstantDeathAction(BaseModel):
    """Threshold death with an optional source-neutral fallback damage payload."""

    id: str
    name: str
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    max_current_hp: int = Field(ge=1)
    fallback_damage_dice_count: int = Field(default=0, ge=0, le=40)
    fallback_damage_dice_size: int = Field(default=0, ge=0, le=100)
    fallback_damage_bonus: int = 0
    fallback_damage_type: DamageTypeName | None = None
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    magical_effect: bool = True
    animation: str = "instant-death"

    @model_validator(mode="after")
    def validate_fallback_damage(self) -> "HpThresholdInstantDeathAction":
        configured = (
            self.fallback_damage_dice_count > 0,
            self.fallback_damage_dice_size > 0,
            self.fallback_damage_type is not None,
        )
        if any(configured) and not all(configured):
            raise ValueError("Threshold fallback damage requires dice count, die size, and damage type.")
        if self.fallback_damage_dice_size == 1:
            raise ValueError("Threshold fallback damage die size must be at least 2.")
        return self
