from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons_base import DamageType


class TimedFriendlyWeaponDamageAura(BaseModel):
    """Live friendly aura that adds printed weapon/Unarmed Strike damage."""

    radius_ft: int = Field(ge=1, le=120)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType


class TimedFriendlyRecoveryAura(BaseModel):
    """Live friendly aura for printed healing, necrotic Resistance, and HP-max lock."""

    radius_ft: int = Field(ge=1, le=120)
    heal_dice_count: int = Field(default=0, ge=0, le=40)
    heal_dice_size: int = Field(default=6, ge=2, le=100)
    heal_flat: int = Field(default=0, ge=0, le=500)
    heal_on_create: bool = False
    heal_on_source_turn_start: bool = False
    zero_hp_ally_start_heal: int = Field(default=0, ge=0, le=20)
    necrotic_resistance: bool = False
    prevent_hp_maximum_reduction: bool = False

    @model_validator(mode="after")
    def validate_recovery(self) -> "TimedFriendlyRecoveryAura":
        if not (
            self.heal_dice_count
            or self.heal_flat
            or self.zero_hp_ally_start_heal
            or self.necrotic_resistance
            or self.prevent_hp_maximum_reduction
        ):
            raise ValueError("Friendly recovery aura requires a printed recovery or defense.")
        if (self.heal_on_create or self.heal_on_source_turn_start) and not (
            self.heal_dice_count or self.heal_flat
        ):
            raise ValueError("Recovery-aura healing windows require printed heal dice or flat HP.")
        return self
