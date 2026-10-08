from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class TurnStartPersistentEffectRule(BaseModel):
    """Immutable source parameters for a turn-start persistent effect trigger."""

    source_id: str
    source_name: str
    effect_id: str
    max_current_hp: int = Field(ge=1)
    die_size: int = Field(default=6, ge=2, le=100)
    minimum_roll: int = Field(ge=1)
    ends_on_full_hp: bool = True

    @model_validator(mode="after")
    def validate_trigger(self) -> "TurnStartPersistentEffectRule":
        try:
            if self.minimum_roll > self.die_size:
                raise ValueError("Turn-start effect trigger cannot exceed its die size.")
            if not self.effect_id.strip():
                raise ValueError("Turn-start persistent effect requires an effect id.")
            return self
        except Exception:
            logger.exception("Invalid turn-start persistent effect rule for %s.", self.source_id)
            raise
