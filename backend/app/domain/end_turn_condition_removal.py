from __future__ import annotations

from pydantic import BaseModel, Field


class EndTurnConditionRemovalGrant(BaseModel):
    """Automatically remove the first active condition from a declared priority list."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    condition_ids: list[str] = Field(min_length=1)
    max_conditions: int = Field(default=1, ge=1, le=20)
