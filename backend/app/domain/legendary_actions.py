from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

LegendaryActionKind = Literal["attack", "saving_throw", "spell_attack", "spell_save", "automatic", "movement"]


class LegendaryActionOption(BaseModel):
    """Immutable source-derived option executed after another creature's turn."""

    id: str
    name: str
    kind: LegendaryActionKind
    action_id: str
    cost: int = Field(default=1, ge=1, le=10)
    once_until_owner_turn: bool = False


class LegendaryActionPool(BaseModel):
    """Immutable legendary-action economy carried by a combatant template."""

    max_uses: int = Field(ge=1, le=10)
    options: list[LegendaryActionOption] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_options(self) -> "LegendaryActionPool":
        option_ids = [option.id for option in self.options]
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("Legendary action option ids must be unique.")
        if any(option.cost > self.max_uses for option in self.options):
            raise ValueError("Legendary action option cost cannot exceed the pool maximum.")
        return self
