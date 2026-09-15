from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons import DamageType


class DamageTriggeredRollPenalty(BaseModel):
    """Declarative roll penalty activated when specified damage is actually taken."""

    id: str = Field(min_length=1)
    damage_types: list[DamageType] = Field(min_length=1)
    attack_roll_disadvantage: bool = False
    ability_check_disadvantage: bool = False
    expires_after_next_target_turn: bool = True

    @model_validator(mode="after")
    def validate_penalty(self) -> "DamageTriggeredRollPenalty":
        if not (self.attack_roll_disadvantage or self.ability_check_disadvantage):
            raise ValueError("Damage-triggered roll penalty must affect at least one roll family.")
        if len(self.damage_types) != len(set(self.damage_types)):
            raise ValueError("Damage-triggered roll penalty damage types must be unique.")
        return self
