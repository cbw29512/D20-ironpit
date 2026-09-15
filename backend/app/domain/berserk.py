from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class BerserkProfile(BaseModel):
    hp_threshold: int = Field(ge=1)
    die_size: int = Field(default=6, ge=2, le=100)
    trigger_roll: int = Field(default=6, ge=1)
    effect_id: str = "berserk"

    @model_validator(mode="after")
    def validate_trigger(self) -> "BerserkProfile":
        if self.trigger_roll > self.die_size:
            raise ValueError("Berserk trigger roll cannot exceed its die size.")
        return self
