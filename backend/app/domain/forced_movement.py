from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize

ForcedMovementDirection = Literal["push", "pull"]


class ForcedMovement(BaseModel):
    direction: ForcedMovementDirection
    distance_ft: int = Field(gt=0, le=120)
    max_target_size: CreatureSize | None = None
