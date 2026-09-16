from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName
from app.domain.size import CreatureSize
from app.domain.weapons_base import DamageType

ChargeFollowUpActionCost = Literal["free", "bonus_action"]


class ChargeDamage(BaseModel):
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    damage_bonus: int = 0


class AttackChargeProfile(BaseModel):
    minimum_move_ft: int = Field(ge=0)
    max_target_size: CreatureSize | None = None
    prone_max_target_size: CreatureSize | None = None
    prone_save_ability: AbilityName | None = None
    prone_save_dc: int | None = Field(default=None, ge=1, le=40)
    bonus_damage: ChargeDamage | None = None
    replacement_damage: ChargeDamage | None = None
    follow_up_attack_id: str | None = None
    follow_up_required_target_condition: ConditionName | None = None
    follow_up_action_cost: ChargeFollowUpActionCost = "free"

    @model_validator(mode="after")
    def validate_shape(self) -> "AttackChargeProfile":
        if (self.prone_save_ability is None) != (self.prone_save_dc is None):
            raise ValueError("Charge Prone save ability and DC must be declared together.")
        if self.follow_up_attack_id is None and (
            self.follow_up_required_target_condition is not None or self.follow_up_action_cost != "free"
        ):
            raise ValueError("Charge follow-up requirements need a follow-up attack id.")
        return self
