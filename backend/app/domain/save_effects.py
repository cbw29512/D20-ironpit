from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.rule_types import AbilityName, ConditionName, ConditionTiming, DamageTypeName
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


class PeriodicDamageEffectDefinition(BaseModel):
    """Damage that repeats while its owning timed condition remains active."""

    timing: Literal["target_turn_start", "target_turn_end"]
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName


class ConditionEffectDefinition(BaseModel):
    kind: Literal["condition"] = "condition"
    condition: ConditionName
    max_target_size: CreatureSize | None = None
    linked_conditions: list[ConditionName] = Field(default_factory=list)
    expires_at_start_of_source_turn: bool = False
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    repeat_save_delay_rounds: int = Field(default=0, ge=0, le=20)
    repeat_save_failure_condition: ConditionName | None = None
    automatic_success_after_rounds: int | None = Field(default=None, ge=1, le=100)
    allowed_removal_action_ids: list[str] = Field(default_factory=list)
    periodic_damage: PeriodicDamageEffectDefinition | None = None

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "ConditionEffectDefinition":
        repeat = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
        if any(item is not None for item in repeat) and not all(item is not None for item in repeat):
            raise ValueError("Condition repeat save requires ability, DC, and timing together.")
        if self.repeat_save_delay_rounds and not all(item is not None for item in repeat):
            raise ValueError("Condition repeat-save delay requires a complete repeat-save rule.")
        if self.repeat_save_failure_condition and not all(item is not None for item in repeat):
            raise ValueError("Repeat-save failure condition requires a complete repeat-save rule.")
        if self.automatic_success_after_rounds and not all(item is not None for item in repeat):
            raise ValueError("Automatic repeat-save success requires a complete repeat-save rule.")
        if self.condition in self.linked_conditions:
            raise ValueError("A linked condition cannot duplicate its owning condition.")
        if self.expires_at_start_of_source_turn and self.expiry_timing not in {None, "source_turn_start"}:
            raise ValueError("Legacy source-start expiry conflicts with explicit condition timing.")
        return self


class TurnRestrictionEffectDefinition(BaseModel):
    kind: Literal["turn-restriction"] = "turn-restriction"
    action_or_bonus_only: bool = False
    reactions_disabled: bool = False
    speed_multiplier: float = Field(default=1.0, gt=0, le=1.0)
    requires_condition: ConditionName | None = None
    expiry_timing: ConditionTiming

    @model_validator(mode="after")
    def require_restriction(self) -> "TurnRestrictionEffectDefinition":
        if not self.action_or_bonus_only and not self.reactions_disabled and self.speed_multiplier == 1.0:
            raise ValueError("Turn restriction must restrict action economy or speed.")
        return self


class TimedPenaltyEffectDefinition(BaseModel):
    """Reusable failed-save penalty with repeat-save recovery."""

    kind: Literal["timed-penalty"] = "timed-penalty"
    effect_family: str | None = None
    d20_disadvantage_ability: AbilityName | None = None
    damage_penalty_dice_count: int = Field(default=0, ge=0, le=4)
    damage_penalty_dice_size: int = Field(default=6, ge=2, le=20)
    repeat_save_ability: AbilityName
    repeat_save_dc: int = Field(ge=1, le=40)
    repeat_save_timing: ConditionTiming
    automatic_success_after_rounds: int | None = Field(default=None, ge=1, le=100)

    @model_validator(mode="after")
    def require_penalty(self) -> "TimedPenaltyEffectDefinition":
        if self.d20_disadvantage_ability is None and not self.damage_penalty_dice_count:
            raise ValueError("Timed penalty must affect a D20 Test or damage roll.")
        return self


SaveFailureEffectDefinition = Annotated[
    ProneEffectDefinition
    | GrappleEffectDefinition
    | ConditionEffectDefinition
    | TurnRestrictionEffectDefinition
    | TimedPenaltyEffectDefinition
    | CombatModifierEffect,
    Field(discriminator="kind"),
]
