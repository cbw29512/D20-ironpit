from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost
from app.domain.save_damage import DamageTypeName


class TargetedConcentrationDamageAction(BaseModel):
    """A no-save hostile-target spell that adds damage to the caster's attacks while Concentrating."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "bonus_action"
    range_ft: int = Field(ge=0)
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageTypeName
    duration_rounds_by_slot: dict[int, int] = Field(min_length=1)
    retarget_after_target_zero: bool = True
    priority: int = 0
    animation: str = "targeted-concentration"
    source: str | None = None

    @model_validator(mode="after")
    def validate_slot_durations(self) -> "TargetedConcentrationDamageAction":
        if self.action_cost != "bonus_action":
            raise ValueError("Targeted concentration damage currently requires a Bonus Action.")
        if any(level < self.level or level > 9 for level in self.duration_rounds_by_slot):
            raise ValueError("Targeted concentration duration slots must be legal for the printed spell level.")
        if any(rounds < 1 for rounds in self.duration_rounds_by_slot.values()):
            raise ValueError("Targeted concentration durations must be positive.")
        return self

    def duration_rounds(self, slot_level: int) -> int:
        eligible = [
            (level, rounds)
            for level, rounds in self.duration_rounds_by_slot.items()
            if level <= slot_level
        ]
        if not eligible:
            raise ValueError(f"{self.name} has no duration rule for slot level {slot_level}.")
        return max(eligible, key=lambda item: item[0])[1]
