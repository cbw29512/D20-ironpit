from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize
from app.domain.weapons import DamageType


class SwallowAction(BaseModel):
    id: str = "swallow"
    name: str = "Swallow"
    attack_id: str
    max_target_size: CreatureSize
    damage_dice_count: int = Field(ge=1, le=40)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.ACID
    max_swallowed: int = Field(default=1, ge=1, le=8)
    exit_movement_ft: int = Field(default=5, ge=0, le=60)
    exit_prone: bool = True


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
