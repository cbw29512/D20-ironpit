from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionTiming

logger = logging.getLogger(__name__)


class OnHitTimedEffect(BaseModel):
    """Source-neutral timed effect applied after a successful hit."""

    effect_id: str
    duration_rounds: int = Field(default=1, ge=1, le=14400)
    expiry_timing: ConditionTiming = "source_turn_start"
    suppress_action: bool = False
    suppress_bonus_action: bool = False
    suppress_reactions: bool = False
    suppress_movement: bool = False
    next_attack_disadvantage: bool = False
    source_is_magical: bool = True
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None

    @model_validator(mode="after")
    def validate_repeat_save(self) -> "OnHitTimedEffect":
        try:
            fields = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
            if any(item is not None for item in fields) and not all(
                item is not None for item in fields
            ):
                raise ValueError(
                    "On-hit timed effect repeat save requires ability, DC, and timing."
                )
            return self
        except Exception:
            logger.exception(
                "Invalid repeat-save payload for on-hit timed effect %s.",
                self.effect_id,
            )
            raise
