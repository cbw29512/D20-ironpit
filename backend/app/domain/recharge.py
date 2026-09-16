from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class RechargeRule(BaseModel):
    """Immutable source definition for a d6 Recharge resource."""

    resource_id: str
    minimum_roll: int = Field(ge=1, le=6)
    die_size: int = Field(default=6, ge=2, le=100)

    @model_validator(mode="after")
    def validate_threshold(self) -> "RechargeRule":
        try:
            if self.minimum_roll > self.die_size:
                raise ValueError("Recharge threshold cannot exceed the recharge die size.")
            return self
        except Exception:
            logger.exception("Invalid Recharge rule for resource %s.", self.resource_id)
            raise
