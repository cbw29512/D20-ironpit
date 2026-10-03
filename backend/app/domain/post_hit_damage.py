from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost
from app.domain.character_builds import AbilityName


class PostHitFailedSave(BaseModel):
    """Save resolved after post-hit damage is part of the triggering attack."""

    save_ability: AbilityName
    dc_ability: AbilityName
    push_ft: int = Field(default=0, ge=0, le=120)
    condition_id: str | None = None

    @model_validator(mode="after")
    def require_outcome(self) -> "PostHitFailedSave":
        if self.push_ft % 5:
            raise ValueError("Post-hit failed-save push must be a multiple of 5 feet.")
        if self.push_ft == 0 and self.condition_id is None:
            raise ValueError("Post-hit failed save requires a push, a condition, or both.")
        return self


class ResourceBackedPostHitDamage(BaseModel):
    """Generic damage cast immediately after a qualifying successful attack."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    trigger_attack_ids: list[str] = Field(min_length=1)
    action_cost: ActionCost = "bonus_action"
    free_resource_id: str | None = None
    printed_spell_level: int = Field(default=1, ge=1, le=9)
    max_slot_level: int = Field(default=9, ge=1, le=9)
    base_dice_count: int = Field(ge=1, le=40)
    dice_per_slot_above: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: str = Field(min_length=1)
    bonus_target_creature_types: list[str] = Field(default_factory=list)
    bonus_target_dice_count: int = Field(default=0, ge=0, le=20)
    doubles_on_critical: bool = True
    failed_save: PostHitFailedSave | None = None
