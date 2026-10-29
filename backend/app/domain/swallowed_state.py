"""Encounter-only ownership of a swallowed creature.

No monster-name rules, grid resizing, or permanent card mutations. An action
must have already resolved a successful printed Bite against a held target.
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from app.domain.size import CreatureSize


class SwallowedState(BaseModel):
    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    damage_dice_count: int = Field(ge=1)
    damage_dice_size: int = Field(ge=2)
    damage_type: str = Field(min_length=1)
    exit_movement_ft: int = Field(ge=0)
    target_size: CreatureSize
