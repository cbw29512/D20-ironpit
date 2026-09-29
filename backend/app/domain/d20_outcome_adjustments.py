from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class ResourceBackedD20OutcomeAdjustment(BaseModel):
    """Resource-backed adjustment applied after a D20 Test succeeds or fails."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1, le=20)
    dice_count: int = Field(default=1, ge=1, le=10)
    dice_size: int = Field(default=4, ge=2, le=100)
    range_ft: int = Field(default=60, ge=0)
    test_kinds: list[Literal["attack", "saving_throw", "ability_check"]] = Field(min_length=1)
    can_add: bool = True
    can_subtract: bool = True

    @model_validator(mode="after")
    def validate_adjustment(self) -> "ResourceBackedD20OutcomeAdjustment":
        try:
            if not self.can_add and not self.can_subtract:
                raise ValueError(
                    "D20 outcome adjustment must allow addition, subtraction, or both."
                )
            if len(set(self.test_kinds)) != len(self.test_kinds):
                raise ValueError("D20 outcome adjustment test kinds must be unique.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception(
                "Failed to validate D20 outcome adjustment %s.", self.source_id
            )
            raise ValueError("D20 outcome adjustment validation failed.") from exc
