from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import SavingThrowAction


class LegendaryActionOption(BaseModel):
    """One printed legendary action that spends the shared after-turn pool."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    cost: int = Field(default=1, ge=1, le=6)
    kind: Literal["attack", "save"] = "attack"
    attack_id: str | None = Field(default=None, min_length=1)
    save_action: SavingThrowAction | None = None

    @model_validator(mode="after")
    def validate_kind(self) -> "LegendaryActionOption":
        if self.kind == "attack":
            if not self.attack_id:
                raise ValueError("Attack-kind legendary action requires attack_id.")
            if self.save_action is not None:
                raise ValueError("Attack-kind legendary action cannot carry a save action.")
        if self.kind == "save":
            if self.save_action is None or self.save_action.area is None:
                raise ValueError("Save-kind legendary action requires an area save action.")
            if self.attack_id:
                raise ValueError("Save-kind legendary action cannot reference an attack.")
        return self
