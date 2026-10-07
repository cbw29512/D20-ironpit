from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class TurnStartTargetingOverrideRule(BaseModel):
    """Immutable source parameters for a persistent targeting-policy override."""

    source_id: str
    source_name: str
    max_current_hp: int = Field(ge=1)
    die_size: int = Field(default=6, ge=2, le=100)
    minimum_roll: int = Field(ge=1)
    target_mode: Literal["nearest_visible_creature"] = "nearest_visible_creature"
    ends_on_full_hp: bool = True

    @model_validator(mode="after")
    def validate_threshold(self) -> "TurnStartTargetingOverrideRule":
        try:
            if self.minimum_roll > self.die_size:
                raise ValueError("Targeting-override trigger cannot exceed its die size.")
            return self
        except Exception:
            logger.exception("Invalid targeting override rule for %s.", self.source_id)
            raise
