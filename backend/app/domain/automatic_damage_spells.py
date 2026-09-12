from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, DamageTypeName


class AutomaticDamageSpellAction(BaseModel):
    """A spell that deals damage without an attack roll or saving throw."""

    id: str
    name: str
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    base_projectiles: int = Field(default=1, ge=1, le=40)
    projectiles_per_slot_above: int = Field(default=0, ge=0, le=20)
    damage_dice_count_per_projectile: int = Field(default=1, ge=1, le=10)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus_per_projectile: int = 0
    damage_type: DamageTypeName
    animation: str = "automatic-damage-spell"
    source: str | None = None

    @model_validator(mode="after")
    def validate_projectiles(self) -> "AutomaticDamageSpellAction":
        if self.projectiles_per_slot_above and self.level >= 9:
            raise ValueError("A level 9 spell cannot scale through higher spell slots.")
        return self

    def projectile_count(self, slot_level: int) -> int:
        if slot_level < self.level:
            raise ValueError(f"{self.name} requires at least a level {self.level} slot.")
        return self.base_projectiles + (slot_level - self.level) * self.projectiles_per_slot_above
