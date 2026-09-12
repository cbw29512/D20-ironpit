from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName
from app.domain.size import CreatureSize
from app.domain.weapons_types import DamageTypeName


class ChargeDamageDefinition(BaseModel):
    dice_count: int = Field(ge=0, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageTypeName
    damage_bonus: int = 0


class ChargeProfileDefinition(BaseModel):
    minimum_move_ft: int = Field(ge=0)
    max_target_size: CreatureSize | None = None
    prone_max_target_size: CreatureSize | None = None
    prone_save_ability: AbilityName | None = None
    prone_save_dc: int | None = Field(default=None, ge=1, le=40)
    bonus_damage: ChargeDamageDefinition | None = None
    replacement_damage: ChargeDamageDefinition | None = None
    follow_up_attack_id: str | None = None

    @model_validator(mode="after")
    def validate_prone_save(self) -> "ChargeProfileDefinition":
        if (self.prone_save_ability is None) != (self.prone_save_dc is None):
            raise ValueError("Charge prone save requires both ability and DC.")
        return self
