from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.character_builds import AbilityName


class DamagingActionTemporaryHpRider(BaseModel):
    """Grant ability-scaled Temporary HP after a declared damaging action succeeds."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    action_ids: list[str] = Field(min_length=1)
    ability: AbilityName
    multiplier: int = Field(default=1, ge=1, le=10)
    range_ft: int = Field(default=0, ge=0)
    target_mode: Literal["self", "self_or_ally"] = "self"
