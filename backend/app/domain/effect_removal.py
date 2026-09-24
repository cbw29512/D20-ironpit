from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost

EffectRemovalTargetMode = Literal["enemy", "ally", "self_or_ally", "any"]


class EffectRemovalAction(BaseModel):
    """A spell/action that can end a tracked persistent spell effect."""

    id: str
    name: str
    level: int = Field(default=0, ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    casting_ability: AbilityName | None = None
    target_mode: EffectRemovalTargetMode = "enemy"
    auto_remove_max_level: int = Field(default=3, ge=0, le=9)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    expends_spell_slot: bool = False
    animation: str = "effect-removal"

    @model_validator(mode="after")
    def validate_resource(self) -> "EffectRemovalAction":
        slot_resource = bool(self.resource_id and self.resource_id.startswith("spell-slot-"))
        if slot_resource != self.expends_spell_slot:
            raise ValueError("Spell-slot resource and expends_spell_slot must agree.")
        if self.auto_remove_max_level < 9 and self.casting_ability is None:
            raise ValueError("Effect removal that can require a spell-level check needs a casting ability.")
        return self
