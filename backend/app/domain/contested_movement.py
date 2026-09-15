from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName
from app.domain.size import CreatureSize


class OnHitContestedMovement(BaseModel):
    source_ability: AbilityName
    target_ability: AbilityName
    max_target_size: CreatureSize | None = None
    distance_ft: int = Field(ge=5, le=120, multiple_of=5)
    direction: Literal["toward_source", "away_from_source"] = "toward_source"
