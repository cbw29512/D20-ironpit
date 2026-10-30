from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.combatants import DamageType

logger = logging.getLogger(__name__)


class TimedDamageEffect(BaseModel):
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType

    @model_validator(mode="after")
    def validate_damage(self) -> "TimedDamageEffect":
        try:
            return self
        except Exception:
            logger.exception("Timed damage effect validation failed.")
            raise
