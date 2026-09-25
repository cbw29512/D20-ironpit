from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost

logger = logging.getLogger(__name__)

D20TestKind = Literal["attack", "saving_throw", "ability_check"]
D20BonusTargetMode = Literal["other_ally", "ally", "self"]


class D20BonusDieAction(BaseModel):
    """Grant one finite-duration die that the recipient may spend on a supported d20 test."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    action_cost: ActionCost
    range_ft: int = Field(ge=0, le=600)
    target_mode: D20BonusTargetMode = "other_ally"
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1, le=200)
    dice_count: int = Field(default=1, ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    test_kinds: list[D20TestKind] = Field(min_length=1)
    duration_rounds: int = Field(ge=1, le=600)
    priority: int = 0
    animation: str = "inspiration"

    @model_validator(mode="after")
    def validate_test_kinds(self) -> "D20BonusDieAction":
        try:
            if len(set(self.test_kinds)) != len(self.test_kinds):
                raise ValueError("D20 bonus-die test kinds must be unique.")
            if self.target_mode == "self" and self.range_ft != 0:
                raise ValueError("Self-targeted d20 bonus-die actions must use zero range.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("D20 bonus-die action validation failed for %s.", self.id)
            raise RuntimeError("D20 bonus-die action could not be validated.") from exc
