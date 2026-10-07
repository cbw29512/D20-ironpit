from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class TurnStartTargetingOverrideRule(BaseModel):
    """Immutable trigger/lifecycle parameters for a persistent targeting override."""

    source_id: str
    source_name: str
    max_current_hp: int = Field(ge=1)
    die_size: int = Field(default=6, ge=2, le=100)
    minimum_roll: int = Field(ge=1)
    ends_on_full_hp: bool = True

    @model_validator(mode="after")
    def validate_trigger(self) -> "TurnStartTargetingOverrideRule":
        try:
            if self.minimum_roll > self.die_size:
                raise ValueError("Targeting-override trigger cannot exceed its die size.")
            return self
        except Exception:
            logger.exception("Invalid targeting-override trigger for %s.", self.source_id)
            raise
