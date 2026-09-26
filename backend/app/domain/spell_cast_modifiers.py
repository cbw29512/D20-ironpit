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
