from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.size import CreatureSize
from app.domain.weapons import DamageType


class ChargeDamage(BaseModel):
    dice_count: int = Field(ge=0, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    damage_bonus: int = 0


class ChargeDefinition(BaseModel):
    """Source-neutral Charge parameters carried by an attack, never inferred from its id."""

    minimum_move_ft: int = Field(ge=0)
    max_target_size: CreatureSize | None = None
    prone_max_target_size: CreatureSize | None = None
    bonus_damage: ChargeDamage | None = None
    replacement_damage: ChargeDamage | None = None
    follow_up_attack_id: str | None = None

    @model_validator(mode="after")
    def validate_charge(self) -> "ChargeDefinition":
        if self.bonus_damage is not None and self.replacement_damage is not None:
            raise ValueError("Charge cannot both add and replace the attack's damage.")
        if not any((
            self.prone_max_target_size is not None,
            self.bonus_damage is not None,
            self.replacement_damage is not None,
            self.follow_up_attack_id is not None,
        )):
            raise ValueError("Charge must define an outcome-changing combat consequence.")
        return self
