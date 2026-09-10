from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.size import CreatureSize


class ChargeDamage(BaseModel):
    dice_count: int = Field(ge=0, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: str
    damage_bonus: int = 0


class ChargeProfile(BaseModel):
    minimum_move_ft: int = Field(ge=5, le=120)
    max_target_size: CreatureSize | None = None
    prone_max_target_size: CreatureSize | None = None
    bonus_damage: ChargeDamage | None = None
    replacement_damage: ChargeDamage | None = None
    follow_up_attack_id: str | None = None

    @model_validator(mode="after")
    def validate_profile(self) -> "ChargeProfile":
        if self.minimum_move_ft % 5:
            raise ValueError("Charge movement must use 5-foot increments.")
        return self
