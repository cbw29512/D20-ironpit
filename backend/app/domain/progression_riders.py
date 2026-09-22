from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.character_builds import AbilityName


class D20OutcomeAdjustmentRule(BaseModel):
    """Post-result D20 adjustment available to creatures within a declared range."""

    source_id: str
    resource_id: str
    range_ft: int = Field(ge=0)
    dice_count: int = Field(ge=1, le=10)
    dice_size: int = Field(ge=2, le=100)


class HealingDiceMaximizer(BaseModel):
    """Maximize healing dice for an explicit set of healing source ids."""

    source_id: str
    healing_source_ids: list[str] = Field(min_length=1)


class DamagingActionTemporaryHpRider(BaseModel):
    """Grant ability-scaled Temporary HP after a declared action deals damage."""

    source_id: str
    action_ids: list[str] = Field(min_length=1)
    ability: AbilityName
    multiplier: int = Field(default=1, ge=1, le=10)
