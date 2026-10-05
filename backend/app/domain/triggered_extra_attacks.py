from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons import DamageType, WeaponAttack


class TriggeredExtraAttackStack(BaseModel):
    """Stackable source-owned state that can add off-turn attacks after the owner's turn."""

    source_id: str
    source_name: str
    trigger_damage_type: DamageType
    trigger_damage_minimum: int = Field(ge=1)
    requires_bloodied: bool = False
    max_stacks: int = Field(ge=1, le=20)
    max_uses: int = Field(ge=1, le=20)
    exhaustion_per_stack: int = Field(default=0, ge=0, le=6)
    attack: WeaponAttack
    clears_on_regeneration_heal: bool = False

    @model_validator(mode="after")
    def validate_limits(self) -> "TriggeredExtraAttackStack":
        if self.max_uses < self.max_stacks:
            raise ValueError("Triggered extra-attack max uses cannot be lower than max stacks.")
        return self
