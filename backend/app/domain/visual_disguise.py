"""Source-declared visual disguise; identical schema for monsters and pregens."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class VisualDisguiseAction(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    activation_cost: Literal["action"] = "action"
    dismissal_cost: Literal["bonus_action"] = "bonus_action"
    conceals_true_form: bool = True
    magical_illusion: bool = True
    ends_if_owner_dead: bool = True
    inspection_cost: Literal["action"] = "action"
    inspection_ability: Literal["intelligence"] = "intelligence"
    inspection_skill: Literal["investigation"] = "investigation"
    inspection_dc: int = Field(ge=1, le=40)
    investigation_reveals_true_form: bool = False
    opening_priority: int = 20
    opening_eligible: bool = True
    dismiss_on_first_turn: bool = True
