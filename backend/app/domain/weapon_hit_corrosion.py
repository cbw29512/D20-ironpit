"""Declarative, source-owned corrosion trigger; equipment evidence remains separate."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class WeaponHitCorrosionRule(BaseModel):
    source_name: str = Field(min_length=1)
    qualifying_materials: list[Literal["metal", "wood"]] = Field(min_length=1)
    requires_nonmagical: bool = True
    penalty_per_hit: Literal[1] = 1
    unusable_at_penalty: Literal[5] = 5
    fight_only: Literal[True] = True
