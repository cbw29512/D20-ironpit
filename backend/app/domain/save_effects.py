from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.rule_types import AbilityName, ConditionName, ConditionTiming
from app.domain.size import CreatureSize


class ProneEffectDefinition(BaseModel):
    kind: Literal["prone"] = "prone"
    max_target_size: CreatureSize | None = None


class GrappleEffectDefinition(BaseModel):
    kind: Literal["grapple"] = "grapple"
    escape_dc: int = Field(ge=1, le=40)
    max_target_size: CreatureSize | None = None
    restrains: bool = False
    linked_conditions: list[ConditionName] = Field(default_factory=list)


class ConditionEffectDefinition(BaseModel):
    kind: Literal["condition"] = "condition"
    condition: ConditionName
    max_target_size: CreatureSize | None = None
    expires_at_start_of_source_turn: bool = False
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    repeat_save_delay_rounds: int = Field(default=0, ge=0, le=20)
    allowed_removal_action_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "ConditionEffectDefinition":
        repeat = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
        if any(item is not None for item in repeat) and not all(item is not None for item in repeat):
            raise ValueError("Condition repeat save requires ability, DC, and timing together.")
        if self.repeat_save_delay_rounds and not all(item is not None for item in repeat):
            raise ValueError("Condition repeat-save delay requires a complete repeat-save rule.")
        if self.expires_at_start_of_source_turn and self.expiry_timing not in {None, "source_turn_start"}:
            raise ValueError("Legacy source-start expiry conflicts with explicit condition timing.")
        return self


class TurnRestrictionEffectDefinition(BaseModel):
    kind: Literal["turn-restriction"] = "turn-restriction"
    action_or_bonus_only: bool = False
    reactions_disabled: bool = False
    expiry_timing: ConditionTiming

    @model_validator(mode="after")
    def require_restriction(self) -> "TurnRestrictionEffectDefinition":
        if not self.action_or_bonus_only and not self.reactions_disabled:
            raise ValueError("Turn restriction must disable or restrict at least one action type.")
        return self


SaveFailureEffectDefinition = Annotated[
    ProneEffectDefinition
    | GrappleEffectDefinition
    | ConditionEffectDefinition
    | TurnRestrictionEffectDefinition
    | CombatModifierEffect,
    Field(discriminator="kind"),
]
