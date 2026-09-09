from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

AbilityName = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


class EffectGate(BaseModel):
    """Data-only requirements evaluated before an effect can fire."""

    required_target_tags: list[str] = Field(default_factory=list)
    excluded_target_tags: list[str] = Field(default_factory=list)
    excluded_creature_types: list[str] = Field(default_factory=list)
    save_ability: AbilityName | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)

    @model_validator(mode="after")
    def validate_save_gate(self) -> "EffectGate":
        if (self.save_ability is None) != (self.save_dc is None):
            raise ValueError("Effect save gate requires both save ability and DC.")
        return self
