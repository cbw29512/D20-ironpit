from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.character_builds import AbilityName

logger = logging.getLogger(__name__)

SaveEffectTiming = Literal[
    "source_turn_start",
    "source_turn_end",
    "target_turn_start",
    "target_turn_end",
]


class FailedSaveTimedEffect(BaseModel):
    """Source-neutral timed rider applied only after a failed saving throw."""

    effect_id: str
    duration_rounds: int | None = Field(default=None, ge=1, le=100)
    expiry_timing: SaveEffectTiming = "target_turn_end"
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: SaveEffectTiming | None = None
    next_attack_disadvantage: bool = False

    @model_validator(mode="after")
    def validate_repeat_save(self) -> "FailedSaveTimedEffect":
        try:
            configured = (
                self.repeat_save_ability is not None,
                self.repeat_save_dc is not None,
                self.repeat_save_timing is not None,
            )
            if any(configured) and not all(configured):
                raise ValueError("Repeat-save riders require ability, DC, and timing together.")
            return self
        except Exception:
            logger.exception(
                "Failed to validate failed-save timed rider for effect %s.",
                self.effect_id,
            )
            raise
