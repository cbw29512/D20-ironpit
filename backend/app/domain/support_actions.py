from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import ActionCost

SupportTargetMode = Literal["self", "self_or_ally"]


class CombatSupportAction(BaseModel):
    """Non-spell combat support action with temporary HP and timed attack Advantage."""

    id: str
    name: str
    action_cost: ActionCost
    range_ft: int | None = Field(default=None, ge=0)
    target_mode: SupportTargetMode = "self_or_ally"
    temporary_hp_dice_count: int = Field(default=0, ge=0, le=20)
    temporary_hp_dice_size: int = Field(default=6, ge=2, le=100)
    temporary_hp_bonus: int = 0
    attack_roll_advantage_until_source_turn_start: bool = False
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    animation: str = "support"
