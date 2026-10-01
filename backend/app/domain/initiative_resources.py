from __future__ import annotations

from pydantic import BaseModel, Field


class InitiativeHealingRider(BaseModel):
    """Dice-based self-healing that occurs only when the initiative refill resolves."""

    dice_count: int = Field(default=1, ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    healing_bonus: int = Field(default=0, ge=0, le=200)


class InitiativeResourceRefillGrant(BaseModel):
    """Source data for restoring a finite resource when initiative is rolled."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    when_at_or_below: int = Field(default=0, ge=0)
    restore_amount: int = Field(default=1, ge=1, le=200)
    restore_to_max: bool = False
    restore_to_minimum: int | None = Field(default=None, ge=1, le=200)
    usage_resource_id: str | None = None
    usage_resource_cost: int = Field(default=1, ge=1, le=200)
    healing_rider: InitiativeHealingRider | None = None
