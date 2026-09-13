from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.size import CreatureSize
from app.domain.weapons import DamageType


SwallowTrigger = Literal["grappled_action", "hit_failed_save", "hit_grappled"]


class SwallowAction(BaseModel):
    id: str = "swallow"
    name: str = "Swallow"
    attack_id: str
    max_target_size: CreatureSize
    trigger: SwallowTrigger = "grappled_action"
    save_ability: str | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    damage_dice_count: int = Field(ge=1, le=40)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.ACID
    max_swallowed: int | None = Field(default=None, ge=1, le=8)
    exit_movement_ft: int = Field(default=5, ge=0, le=60)
    exit_prone: bool = True
    regurgitate_damage_threshold: int | None = Field(default=None, ge=1)
    regurgitate_save_dc: int | None = Field(default=None, ge=1, le=40)
    regurgitate_on_prone: bool = False
    regurgitate_exit_radius_ft: int = Field(default=10, ge=0, le=60)

    @model_validator(mode="after")
    def validate_trigger(self) -> "SwallowAction":
        if self.trigger == "hit_failed_save" and (not self.save_ability or self.save_dc is None):
            raise ValueError("Save-triggered Swallow requires save_ability and save_dc.")
        if self.trigger != "hit_failed_save" and (self.save_ability or self.save_dc is not None):
            raise ValueError("Only save-triggered Swallow accepts save fields.")
        if (self.regurgitate_damage_threshold is None) != (self.regurgitate_save_dc is None):
            raise ValueError("Regurgitation damage threshold and save DC must be declared together.")
        return self


class SwallowedState(BaseModel):
    source_id: str
    source_effect_id: str
    damage_dice_count: int = Field(ge=1, le=40)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.ACID
    exit_movement_ft: int = Field(default=5, ge=0, le=60)
    exit_prone: bool = True
    source_dead: bool = False
