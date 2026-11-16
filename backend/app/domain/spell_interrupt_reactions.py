"""Source-owned parameters for a universal casting-interruption Reaction."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName


class SpellInterruptReaction(BaseModel):
    """A printed spell-cast trigger, not a monster-specific runtime handler."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    printed_level: int = Field(ge=1, le=9)
    trigger: Literal["visible_spell_cast"] = "visible_spell_cast"
    range_ft: int = Field(gt=0, le=600)
    casting_ability: AbilityName
    resource_prefix: str = "spell-slot-"
    allows_higher_slots: bool = True

    @model_validator(mode="after")
    def validate_resource(self) -> "SpellInterruptReaction":
        if self.resource_prefix != "spell-slot-":
            raise ValueError("Spell interrupt must use certified spell-slot resources.")
        return self
