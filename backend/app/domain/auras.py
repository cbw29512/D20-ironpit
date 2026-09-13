from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName, ConditionTiming


class StartTurnAura(BaseModel):
    id: str
    name: str
    range_ft: int = Field(gt=0)
    save_ability: AbilityName
    save_dc: int = Field(gt=0, le=40)
    failure_condition_id: ConditionName
    failure_expiry_timing: ConditionTiming = "target_turn_start"
    failure_duration_rounds: int = Field(default=1, ge=1, le=100)
    magical_effect: bool = False
    success_grants_source_immunity: bool = False
