from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName
from app.domain.size import CreatureSize


class OnHitSaveEffect(BaseModel):
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition_id: ConditionName
    max_target_size: CreatureSize | None = None
