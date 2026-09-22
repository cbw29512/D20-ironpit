from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.character_builds import AbilityName


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
