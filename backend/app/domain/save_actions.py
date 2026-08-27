from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.abilities import Ability
from app.domain.battlefield_objects import BattlefieldObjectDefinition
from app.domain.conditions import ConditionExpiry, ConditionType
from app.domain.recharge import RechargeDefinition


class SaveFailureEffect(BaseModel):
    effect_type: Literal["condition"] = "condition"
    condition: ConditionType
    expires_on: ConditionExpiry | None = None
    object_definition: BattlefieldObjectDefinition | None = None

    @model_validator(mode="after")
    def validate_termination(self) -> "SaveFailureEffect":
        if self.expires_on is not None and self.object_definition is not None:
            raise ValueError("Condition effect cannot use both turn expiry and object destruction.")
        return self


class SaveAction(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    save_ability: Ability
    dc: int = Field(ge=1, le=40)
    range_ft: int = Field(ge=0, le=1000)
    target_limit: int = Field(default=1, ge=1, le=20)
    failure_effects: list[SaveFailureEffect] = Field(default_factory=list)
    recharge: RechargeDefinition | None = None
    action_cost: Literal["action", "bonus_action", "reaction"] = "action"
    animation: str = "save-action"
