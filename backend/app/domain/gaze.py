from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName


class StartTurnGaze(BaseModel):
    id: str
    name: str
    range_ft: int = Field(gt=0)
    save_ability: AbilityName
    save_dc: int = Field(gt=0, le=40)
    failure_condition_id: ConditionName
    repeat_save_timing: Literal["target_turn_end"] = "target_turn_end"
    repeat_save_failure_condition_id: ConditionName
    immediate_failure_margin: int | None = Field(default=None, ge=1, le=20)
    immediate_failure_condition_id: ConditionName | None = None
    magical_effect: bool = True
    avertible: bool = True
