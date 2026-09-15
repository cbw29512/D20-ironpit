from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType


class SwallowAction(BaseModel):
    id: str = "swallow"
    name: str = "Swallow"
    attack_id: str | None = None
    max_target_size: CreatureSize
    damage_dice_count: int = Field(ge=1, le=40)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.ACID
    max_swallowed: int | None = Field(default=1, ge=1, le=8)
    requires_existing_grapple: bool = True
    start_turn_save_ability: AbilityName | None = None
    start_turn_save_dc: int | None = Field(default=None, ge=1, le=40)
    source_death_release: Literal["corpse_escape", "immediate"] = "corpse_escape"
    regurgitation_damage_threshold: int | None = Field(default=None, ge=1, le=1000)
    regurgitation_save_ability: AbilityName | None = None
    regurgitation_save_dc: int | None = Field(default=None, ge=1, le=40)
    regurgitation_range_ft: int | None = Field(default=None, ge=0, le=120)
    exit_movement_ft: int = Field(default=5, ge=0, le=60)
    exit_prone: bool = True

    @model_validator(mode="after")
    def validate_swallow(self) -> "SwallowAction":
        regurgitation = (
            self.regurgitation_damage_threshold, self.regurgitation_save_ability,
            self.regurgitation_save_dc, self.regurgitation_range_ft,
        )
        if any(item is not None for item in regurgitation) and not all(item is not None for item in regurgitation):
            raise ValueError("Swallow regurgitation requires threshold, save ability, DC, and release range.")
        start_save = (self.start_turn_save_ability, self.start_turn_save_dc)
        if any(item is not None for item in start_save) and not all(item is not None for item in start_save):
            raise ValueError("Containment start-turn damage save requires ability and DC together.")
        return self


class SwallowedState(BaseModel):
    source_id: str
    source_effect_id: str
    damage_dice_count: int = Field(ge=1, le=40)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.ACID
    start_turn_save_ability: AbilityName | None = None
    start_turn_save_dc: int | None = Field(default=None, ge=1, le=40)
    source_death_release: Literal["corpse_escape", "immediate"] = "corpse_escape"
    regurgitation_damage_threshold: int | None = Field(default=None, ge=1, le=1000)
    regurgitation_save_ability: AbilityName | None = None
    regurgitation_save_dc: int | None = Field(default=None, ge=1, le=40)
    regurgitation_range_ft: int | None = Field(default=None, ge=0, le=120)
    exit_movement_ft: int = Field(default=5, ge=0, le=60)
    exit_prone: bool = True
    source_dead: bool = False
