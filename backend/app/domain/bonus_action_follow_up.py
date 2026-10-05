from __future__ import annotations

from pydantic import BaseModel, Field


class BonusActionFollowUpTacticalGrant(BaseModel):
    """Permit one declared tactical grant immediately after another Bonus Action."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    tactical_grant_id: str = Field(min_length=1)
    excluded_trigger_ids: list[str] = Field(default_factory=list)


class BonusActionFollowUpMovementGrant(BaseModel):
    """Grant bounded movement after a declared Bonus Action trigger."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    required_trigger_ids: list[str] = Field(min_length=1)
    speed_fraction: float = Field(gt=0.0, le=1.0)
    desired_distance_ft: int = Field(default=5, ge=0)
    provokes_opportunity_attacks: bool = True
