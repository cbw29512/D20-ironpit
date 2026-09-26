from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ConditionName

logger = logging.getLogger(__name__)

ReactionRollKind = Literal["attack", "ability_check", "damage"]


class ReactionRollPenaltyAction(BaseModel):
    """Reaction that subtracts a die from an observed roll without source-specific dispatch."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    range_ft: int = Field(ge=0, le=600)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1, le=200)
    dice_count: int = Field(default=1, ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    roll_kinds: list[ReactionRollKind] = Field(min_length=1)
    requires_source_sight: bool = False
    requires_target_hearing: bool = False
    blocked_target_condition_immunity: ConditionName | None = None
    priority: int = 0
    animation: str = "reaction"

    @model_validator(mode="after")
    def validate_roll_kinds(self) -> "ReactionRollPenaltyAction":
        try:
            if len(set(self.roll_kinds)) != len(self.roll_kinds):
                raise ValueError("Reaction roll-penalty kinds must be unique.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Reaction roll-penalty validation failed for %s.", self.id)
            raise RuntimeError("Reaction roll-penalty action could not be validated.") from exc
