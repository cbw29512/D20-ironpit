from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

SaveEffectTiming = Literal[
    "source_turn_start",
    "source_turn_end",
    "target_turn_start",
    "target_turn_end",
]


class FailedSaveTimedEffect(BaseModel):
    """Source-neutral timed rider applied only after a failed saving throw."""

    effect_id: str
    expiry_timing: SaveEffectTiming = "target_turn_end"
    duration_rounds: int | None = Field(default=None, ge=1)
    repeat_save_ability: str | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: SaveEffectTiming | None = None
    next_attack_disadvantage: bool = False

    @model_validator(mode="after")
    def validate_repeat_save(self) -> "FailedSaveTimedEffect":
        fields = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
        if any(item is not None for item in fields) and not all(item is not None for item in fields):
            raise ValueError("Failed-save repeat save requires ability, DC, and timing together.")
        return self
