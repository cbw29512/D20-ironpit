from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.abilities import Ability
from app.domain.conditions import ConditionExpiry, ConditionType
from app.domain.creatures import CreatureType


class SizeCategory(StrEnum):
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"


class AttackEffect(BaseModel):
    id: str
    effect_type: Literal["push", "condition", "save_condition"]
    distance_ft: int | None = Field(default=None, ge=1, le=100)
    condition: ConditionType | None = None
    escape_dc: int | None = Field(default=None, ge=1, le=40)
    save_ability: Ability | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    expires_on: ConditionExpiry | None = None
    max_target_size: SizeCategory | None = None
    excluded_creature_types: list[CreatureType] = Field(default_factory=list)
    excluded_creature_tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_effect_payload(self) -> "AttackEffect":
        if self.effect_type == "push" and self.distance_ft is None:
            raise ValueError("Push effects require distance_ft.")
        if self.effect_type in {"condition", "save_condition"} and self.condition is None:
            raise ValueError("Condition effects require a condition.")
        if self.condition is ConditionType.GRAPPLED and self.escape_dc is None:
            raise ValueError("Grappled effects require escape_dc.")
        if self.effect_type == "save_condition" and (
            self.save_ability is None or self.save_dc is None
        ):
            raise ValueError("Save-gated conditions require save ability and DC.")
        return self
