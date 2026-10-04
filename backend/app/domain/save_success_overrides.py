from __future__ import annotations

from pydantic import BaseModel, Field


class FailedSaveSuccessOverride(BaseModel):
    """Spend a resource to turn one failed saving throw into a success."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1, le=20)
