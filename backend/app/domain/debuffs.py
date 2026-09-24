from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

DebuffCounterMode = Literal["prevent", "remove-with-movement"]
DebuffSourceScope = Literal["any", "magical", "nonmagical"]


class DebuffCounter(BaseModel):
    """Declarative rule describing how one active buff counters one debuff."""

    debuff_id: str = Field(min_length=1)
    source_scope: DebuffSourceScope = "any"
    mode: DebuffCounterMode = "prevent"
    movement_cost_ft: int = Field(default=0, ge=0, le=120)

    @model_validator(mode="after")
    def validate_counter(self) -> "DebuffCounter":
        if self.mode == "remove-with-movement":
            if self.movement_cost_ft <= 0 or self.movement_cost_ft % 5:
                raise ValueError("Movement-cost debuff counters require a positive 5-foot increment.")
        elif self.movement_cost_ft:
            raise ValueError("Prevent-mode debuff counters cannot define a movement cost.")
        return self
