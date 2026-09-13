from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, DamageTypeName


class AutomaticSpellAction(BaseModel):
    """A source-driven spell that applies the same automatic effect one or more times."""

    id: str
    name: str
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "action"
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    range_ft: int = Field(ge=0)
    applications: int = Field(ge=1, le=40)
    applications_per_slot_above: int = Field(default=0, ge=0, le=20)
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    allow_split_targets: bool = True
    animation: str = "spell-automatic"
    source: str | None = None

    @model_validator(mode="after")
    def validate_automatic_spell(self) -> "AutomaticSpellAction":
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("Damaging automatic spells require a damage type.")
        return self
