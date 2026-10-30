from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BloodiedBerserkRule(BaseModel):
    """Start-turn Bloodied behavior that can retarget attacks to any nearby creature."""

    id: str
    name: str
    die_size: int = Field(ge=2, le=100)
    trigger_minimum: int = Field(ge=1)
    target_mode: Literal["nearest_living_creature"] = "nearest_living_creature"
    remains_while_bloodied: bool = True
    creator_calming_outside_arena: bool = True
