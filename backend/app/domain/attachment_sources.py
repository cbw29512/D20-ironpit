"""Source-owned on-hit attachment capability, separate from Grappled."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons_base import DamageType
from app.domain.size import CreatureSize


class OnHitAttachment(BaseModel):
    effect_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    periodic_effect_kind: Literal["direct_hp_loss", "typed_damage"] | None = None
    dice_count: int = Field(default=0, ge=0, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType | None = None
    tick_timing: Literal["source_turn_start", "target_turn_start", "target_turn_end"] = "source_turn_start"
    blocks_source_attacks: bool = False
    action_removable: bool = False
    action_removal_range_ft: int = Field(default=5, ge=0)
    source_detach_movement_ft: int = Field(default=0, ge=0)
    auto_end_after_hp_loss: int | None = Field(default=None, ge=1)
    attach_max_target_size: CreatureSize | None = None
    enhanced_on_attack_advantage: bool = False
    enhanced_max_target_size: CreatureSize | None = None
    source_target_lock: bool = False
    source_advantage_against_target: bool = False
    source_speed_zero: bool = False
    moves_with_target: bool = False
    enhanced_blinds_target: bool = False
    enhanced_prevents_breathing: bool = False
    action_removal_check_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"] | None = None
    action_removal_check_dc: int | None = Field(default=None, ge=1, le=40)

    @model_validator(mode="after")
    def validate_source_semantics(self) -> "OnHitAttachment":
        if (self.periodic_effect_kind is None) != (self.dice_count == 0):
            raise ValueError("Only a non-periodic attachment may omit periodic dice.")
        if self.periodic_effect_kind == "direct_hp_loss" and self.damage_type is not None:
            raise ValueError("Direct HP loss must not carry typed damage.")
        if self.periodic_effect_kind == "typed_damage" and self.damage_type is None:
            raise ValueError("Typed attachment damage requires a damage type.")
        if self.source_detach_movement_ft % 5 or self.action_removal_range_ft % 5:
            raise ValueError("Printed detach costs and reach must use 5-foot increments.")
        if (self.action_removal_check_ability is None) != (self.action_removal_check_dc is None):
            raise ValueError("Attachment removal checks require ability and DC together.")
        if (self.enhanced_blinds_target or self.enhanced_prevents_breathing) and not self.enhanced_on_attack_advantage:
            raise ValueError("Enhanced attachment controls require their printed qualifier.")
        return self
