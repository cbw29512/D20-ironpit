from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.size import CreatureSize


class OnHitSaveEffect(BaseModel):
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition_id: ConditionName
    max_target_size: CreatureSize | None = None
    duration_rounds: int | None = Field(default=None, ge=1)
    repeat_save_timing: ConditionTiming | None = None
    ends_on_damage: bool = False
