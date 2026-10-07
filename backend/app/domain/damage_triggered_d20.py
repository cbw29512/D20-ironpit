from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons import DamageType


class DamageTriggeredD20Debuff(BaseModel):
    """Immutable source data for a self-debuff triggered by applied typed damage."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    trigger_damage_type: DamageType
    trigger_damage_minimum: int = Field(default=1, ge=1)
    attack_roll_disadvantage: bool = False
    ability_check_disadvantage: bool = False
    duration_target_turns: int = Field(default=1, ge=1, le=20)

    @model_validator(mode="after")
    def validate_payload(self) -> "DamageTriggeredD20Debuff":
        if not self.attack_roll_disadvantage and not self.ability_check_disadvantage:
            raise ValueError("Damage-triggered D20 debuff requires an attack-roll or ability-check effect.")
        return self


class ActiveDamageTriggeredD20Debuff(BaseModel):
    """Per-fight state for one active damage-triggered D20 debuff."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    attack_roll_disadvantage: bool = False
    ability_check_disadvantage: bool = False
    expires_after_target_turn_count: int = Field(ge=1)
