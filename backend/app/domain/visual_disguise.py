"""Source-declared visual disguise; identical schema for monsters and pregens."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class VisualDisguiseAction(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    # Printed source mechanics: every value is mandatory on the card.
    # No global Sea Hag/monster/pregen defaults belong in the engine.
    activation_cost: Literal["action", "bonus_action"]
    dismissal_cost: Literal["action", "bonus_action"]
    conceals_true_form: bool
    magical_illusion: bool
    ends_if_owner_dead: bool
    physical_inspection_inconsistent: bool
    inspection_cost: Literal["action", "bonus_action"]
    inspection_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    inspection_skill: str = Field(min_length=1)
    inspection_dc: int = Field(ge=1, le=40)
    investigation_reveals_true_form: bool

    # Explicit Iron Pit *tactical choices* attached to a specific compiled
    # card, not RAW mechanics inherent to every magical visual disguise.
    opening_priority: int = Field(ge=0)
    opening_eligible: bool
    dismiss_on_first_turn: bool
