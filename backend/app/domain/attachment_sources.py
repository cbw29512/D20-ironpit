"""Source-owned on-hit attachment capability, separate from Grappled."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons_base import DamageType


class OnHitAttachment(BaseModel):
    effect_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    periodic_effect_kind: Literal["direct_hp_loss", "typed_damage"]
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType | None = None
    tick_timing: Literal["source_turn_start", "target_turn_start", "target_turn_end"]
    blocks_source_attacks: bool = False
    action_removable: bool = False
    action_removal_range_ft: int = Field(default=5, ge=0)
    source_detach_movement_ft: int = Field(default=0, ge=0)
    auto_end_after_hp_loss: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_source_semantics(self) -> "OnHitAttachment":
        if self.periodic_effect_kind == "direct_hp_loss" and self.damage_type is not None:
            raise ValueError("Direct HP loss must not carry typed damage.")
        if self.periodic_effect_kind == "typed_damage" and self.damage_type is None:
            raise ValueError("Typed attachment damage requires a damage type.")
        if self.source_detach_movement_ft % 5 or self.action_removal_range_ft % 5:
            raise ValueError("Printed detach costs and reach must use 5-foot increments.")
        return self
