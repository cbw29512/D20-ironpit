from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import ActionCost
from app.domain.character_builds import AbilityName


class PostHitSpellOption(BaseModel):
    """Bonus Action immediately after a hit: extra damage plus optional printed riders."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "bonus_action"
    trigger_attack_ids: list[str] = Field(min_length=1)
    base_dice_count: int = Field(ge=1, le=40)
    dice_per_slot_above: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: str = Field(min_length=1)
    doubles_on_critical: bool = True
    max_slot_level: int = Field(default=9, ge=1, le=9)
    save_ability: AbilityName | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    failed_condition_id: str | None = None
    failed_condition_expiry_timing: Literal[
        "source_turn_start",
        "source_turn_end",
        "target_turn_start",
        "target_turn_end",
    ] | None = None
    failed_push_ft: int = Field(default=0, ge=0)
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: Literal[
        "source_turn_start",
        "source_turn_end",
        "target_turn_start",
        "target_turn_end",
    ] | None = None
    concentration: bool = False
    duration_rounds: int = Field(default=0, ge=0, le=14400)
    attacks_against_advantage: bool = False
    suppress_invisible: bool = False
    exile_if_hp_at_or_below: int = Field(default=0, ge=0)
