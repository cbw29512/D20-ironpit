from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.rule_types import AbilityName
from app.domain.save_effects import SaveFailureEffectDefinition
from app.domain.target_filters import TargetFilter


class OnHitSavingThrow(BaseModel):
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    magical_effect: bool = False
    target_filter: TargetFilter = Field(default_factory=TargetFilter)
    failure_effects: list[SaveFailureEffectDefinition] = Field(default_factory=list)
    severe_failure_margin: int | None = Field(default=None, ge=1, le=20)
    severe_failure_effects: list[SaveFailureEffectDefinition] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_severe_failure(self) -> "OnHitSavingThrow":
        if (self.severe_failure_margin is None) != (not self.severe_failure_effects):
            raise ValueError("Severe failed-save margin and effects must be configured together.")
        return self
