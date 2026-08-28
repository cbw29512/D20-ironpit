from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.abilities import AbilityKind
from app.domain.events import DiceRoll


class SavingThrowResult(BaseModel):
    ability: AbilityKind
    dc: int = Field(ge=0)
    roll: DiceRoll | None = None
    success: bool
    chosen_failure: bool = False
    automatic_failure: bool = False
    circumstantial_modifier: int = 0
    cover_bonus: int = 0
