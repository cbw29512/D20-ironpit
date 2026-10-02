from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.character_builds import AbilityName


class DeferredSaveEffect(BaseModel):
    """Immutable parameters for a hit-armed effect resolved by a later saving throw."""

    source_id: str
    source_name: str
    trigger_weapon_ids: list[str] = Field(min_length=1)
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)
    save_ability: AbilityName
    save_dc: int = Field(ge=1, le=40)
    failure_sets_zero_hp: bool = False
    failure_damage_dice_count: int = Field(default=0, ge=0, le=40)
    failure_damage_dice_size: int = Field(default=10, ge=2, le=100)
    failure_damage_type: str | None = None
    success_damage_from_failure: Literal["none", "half"] = "none"
    success_damage_dice_count: int = Field(default=0, ge=0, le=40)
    success_damage_dice_size: int = Field(default=10, ge=2, le=100)
    success_damage_type: str | None = None
    allow_attack_slot_activation: bool = False
    allow_harmless_end_on_rearm: bool = False
    max_active_targets: int = Field(default=1, ge=1, le=20)
