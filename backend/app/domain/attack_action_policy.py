from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class AttackActionPolicy(BaseModel):
    distinct_attack_ids: bool = False
    at_most_once_attack_ids: list[str] = Field(default_factory=list)
    repeat_slot_index: int | None = Field(default=None, ge=0, le=7)
    repeat_dice_count: int = Field(default=0, ge=0, le=4)
    repeat_dice_size: int = Field(default=0, ge=0, le=20)
    requires_previous_hit_slots: list[int] = Field(default_factory=list)
    same_target_as_previous_slots: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_repeat(self) -> "AttackActionPolicy":
        values = (self.repeat_slot_index, self.repeat_dice_count, self.repeat_dice_size)
        if any(value not in {None, 0} for value in values) and not (
            self.repeat_slot_index is not None and self.repeat_dice_count > 0 and self.repeat_dice_size > 0
        ):
            raise ValueError("Random Multiattack repetition requires slot index and complete dice expression.")
        if len(self.at_most_once_attack_ids) != len(set(self.at_most_once_attack_ids)):
            raise ValueError("Per-attack Multiattack caps must not contain duplicate ids.")
        return self