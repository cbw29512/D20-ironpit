from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, DamageTypeName


class OngoingDamageEffect(BaseModel):
    id: str
    name: str
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    apply_on: Literal["hit", "failed_on_hit_save"] = "hit"
    stacks_on_reapply: bool = False
    ends_on_magical_healing: bool = False
    ends_when_grapple_source_ends: bool = False
    removal_ability: AbilityName | None = None
    removal_skill: str | None = None
    removal_dc: int | None = Field(default=None, ge=1, le=40)

    @model_validator(mode="after")
    def validate_removal(self) -> "OngoingDamageEffect":
        removal = (self.removal_ability, self.removal_skill, self.removal_dc)
        if any(item is not None for item in removal) and not all(item is not None for item in removal):
            raise ValueError("Ongoing damage removal requires ability, skill, and DC together.")
        return self


class OngoingDamageState(BaseModel):
    source_id: str
    source_effect_id: str
    effect: OngoingDamageEffect
    stacks: int = Field(default=1, ge=1, le=40)
