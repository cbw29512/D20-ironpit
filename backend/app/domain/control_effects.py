from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.size import CreatureSize

AbilityName = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
ConditionTiming = Literal["source_turn_start", "source_turn_end", "target_turn_start", "target_turn_end"]
ConditionName = Literal[
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned", "prone",
    "restrained", "stunned", "unconscious",
]
ForcedMovementDirection = Literal["push", "pull"]
ForcedMovementDistanceMode = Literal["fixed", "up_to"]


class ForcedMovementEffect(BaseModel):
    direction: ForcedMovementDirection
    max_distance_ft: int = Field(ge=5, le=120, multiple_of=5)
    distance_mode: ForcedMovementDistanceMode = "fixed"


class GrappleSource(BaseModel):
    source_id: str
    escape_dc: int = Field(ge=1, le=40)
    range_ft: int = Field(default=5, ge=0)
    restrains: bool = False


class HitControlEffect(BaseModel):
    max_target_size: CreatureSize | None = None
    forced_movement: ForcedMovementEffect | None = None
    grapple_escape_dc: int | None = Field(default=None, ge=1, le=40)
    restrains_while_grappled: bool = False
    condition_id: ConditionName | None = None
    expires_at_start_of_source_turn: bool = False
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    allowed_removal_action_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_condition_lifecycle(self) -> "HitControlEffect":
        repeat_fields = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
        if any(item is not None for item in repeat_fields) and not all(item is not None for item in repeat_fields):
            raise ValueError("Repeat-save condition lifecycle requires ability, DC, and timing together.")
        if self.expires_at_start_of_source_turn and self.expiry_timing not in {None, "source_turn_start"}:
            raise ValueError("Legacy source-start expiry conflicts with explicit condition timing.")
        return self
