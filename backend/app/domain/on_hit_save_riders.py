from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.character_builds import AbilityName


class ResourceBackedOnHitSaveRider(BaseModel):
    """Optional once-per-turn on-hit save with declarative failure and success outcomes."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    trigger_attack_ids: list[str] = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1)
    save_ability: AbilityName
    save_dc: int = Field(ge=1, le=40)
    once_per_turn: bool = True
    failed_condition_id: str | None = None
    failed_condition_expiry_timing: Literal[
        "source_turn_start",
        "source_turn_end",
        "target_turn_start",
        "target_turn_end",
    ] | None = None
    successful_save_speed_multiplier: float | None = Field(default=None, gt=0.0, le=1.0)
    successful_save_next_attack_advantage: bool = False
