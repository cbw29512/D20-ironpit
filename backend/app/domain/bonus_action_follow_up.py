from __future__ import annotations

from pydantic import BaseModel, Field


class BonusActionFollowUpTacticalGrant(BaseModel):
    """Permit one declared tactical grant immediately after another Bonus Action."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    tactical_grant_id: str = Field(min_length=1)
    excluded_trigger_ids: list[str] = Field(default_factory=list)
