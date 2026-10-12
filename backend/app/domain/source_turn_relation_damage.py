"""Immutable source-turn damage targeting a live relationship, not a creature name."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.weapons_base import DamageType


class SourceTurnRelationDamage(BaseModel):
    source_name: str = Field(min_length=1)
    target_relation: Literal["creatures_grappling_source"]
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
