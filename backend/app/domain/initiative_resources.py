from __future__ import annotations

from pydantic import BaseModel, Field


class InitiativeResourceRefillGrant(BaseModel):
    """Source data for restoring a finite resource when initiative is rolled."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    when_at_or_below: int = Field(default=0, ge=0)
    restore_amount: int = Field(ge=1, le=200)
