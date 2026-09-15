from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName, ConditionTiming

AuraActivationCost = Literal["action", "bonus_action"]


class StartTurnAura(BaseModel):
    id: str
    name: str
    range_ft: int = Field(gt=0)
    save_ability: AbilityName
    save_dc: int = Field(gt=0, le=40)
    failure_condition_id: ConditionName
    failure_expiry_timing: ConditionTiming = "target_turn_start"
    failure_duration_rounds: int = Field(default=1, ge=1, le=100)
    failure_blocks_reactions: bool = False
    failure_action_bonus_exclusive: bool = False
    magical_effect: bool = False
    success_grants_source_immunity: bool = False
    reaction_cost: bool = False
    activation_cost: AuraActivationCost | None = None
    activation_duration_rounds: int | None = Field(default=None, ge=1, le=100)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    area_lightly_obscured: bool = False
    spreads_around_corners: bool = False
    dispersed_by_strong_wind: bool = False
