from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ResourceBackedSpellSaveDisadvantage(BaseModel):
    """Spend a finite resource to impose Disadvantage on one target's next spell save."""

    id: str
    name: str
    resource_id: str
    resource_cost: int = Field(ge=1)
    target_policy: Literal["first-target"] = "first-target"
    priority: int = 0
    source: str | None = None


class ResourceBackedSpellRangeModifier(BaseModel):
    """Spend a finite resource only when extra spell range is required."""

    id: str
    name: str
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)
    range_multiplier: int = Field(default=2, ge=1, le=10)
    minimum_base_range_ft: int = Field(default=5, ge=0)
    priority: int = 0
    source: str | None = None
