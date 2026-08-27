from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.conditions import ConditionType


class SizeCategory(StrEnum):
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"


class AttackEffect(BaseModel):
    id: str
    effect_type: Literal["push", "condition"]
    distance_ft: int | None = Field(default=None, ge=1, le=100)
    condition: ConditionType | None = None
    escape_dc: int | None = Field(default=None, ge=1, le=40)
    max_target_size: SizeCategory | None = None

    @model_validator(mode="after")
    def validate_effect_payload(self) -> "AttackEffect":
        if self.effect_type == "push" and self.distance_ft is None:
            raise ValueError("Push effects require distance_ft.")
        if self.effect_type == "condition" and self.condition is None:
            raise ValueError("Condition effects require a condition.")
        if self.condition is ConditionType.GRAPPLED and self.escape_dc is None:
            raise ValueError("Grappled effects require escape_dc.")
        return self
