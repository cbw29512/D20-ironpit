from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class SizeCategory(StrEnum):
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"


class AttackEffect(BaseModel):
    id: str
    effect_type: Literal["push"]
    distance_ft: int = Field(ge=1, le=100)
    max_target_size: SizeCategory | None = None
