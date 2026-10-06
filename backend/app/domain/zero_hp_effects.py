from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import ConditionName


class ZeroHpSaveDamageRider(BaseModel):
    """A source-declared rider that applies only when save damage itself causes 0 HP."""

    stable: Literal[True] = True
    condition_ids: list[ConditionName] = Field(min_length=1)
    duration_rounds: int = Field(ge=1)


class DamageThresholdZeroHpReplacement(BaseModel):
    """Source-owned replacement for a damage drop to 0 HP below a printed threshold."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1)
    max_trigger_damage: int = Field(ge=0)
    replacement_hp: int = Field(ge=1)
