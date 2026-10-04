from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost
from app.domain.character_builds import AbilityName
from app.domain.save_damage import DamageTypeName
from app.domain.size import CreatureSize


class PostHitSaveConditionSpell(BaseModel):
    """Bonus Action after a weapon hit: save, condition, optional start-of-turn damage."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "bonus_action"
    save_ability: AbilityName
    save_dc: int = Field(ge=1, le=40)
    failed_condition_id: str = Field(min_length=1)
    duration_rounds: int = Field(ge=1, le=14400)
    concentration: bool = True
    success_ends_spell: bool = True
    size_save_advantage_from: CreatureSize | None = None
    start_of_turn_dice_count: int = Field(default=0, ge=0, le=40)
    start_of_turn_dice_per_slot_above: int = Field(default=0, ge=0, le=20)
    start_of_turn_dice_size: int = Field(default=6, ge=2, le=100)
    start_of_turn_damage_type: DamageTypeName = "piercing"
    escape_skill: str = "athletics"
    escape_action_cost: ActionCost = "action"
    priority: int = 0
    animation: str = "ensnaring-strike"
    source: str | None = None

    @model_validator(mode="after")
    def validate_printed_lifecycle(self) -> "PostHitSaveConditionSpell":
        if self.action_cost != "bonus_action":
            raise ValueError("Post-hit save-condition spells currently require a Bonus Action.")
        if self.start_of_turn_dice_count < 0:
            raise ValueError("Start-of-turn dice cannot be negative.")
        return self
