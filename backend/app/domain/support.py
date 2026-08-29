from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import ActionCost, HealingTargetMode

SupportEffectName = Literal["bless", "sanctuary"]


class SupportAction(BaseModel):
    """A printed support spell/effect with target, duration, resource, and Concentration rules."""

    id: str
    name: str
    action_cost: ActionCost
    effect_id: SupportEffectName
    range_ft: int = Field(default=30, ge=0)
    target_mode: HealingTargetMode = "self_or_ally"
    max_targets: int = Field(default=1, ge=1, le=20)
    duration_rounds: int = Field(default=10, ge=1, le=100)
    concentration: bool = False
    save_dc: int | None = Field(default=None, ge=1, le=40)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    animation: str = "support"
