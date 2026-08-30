from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost, DamageTypeName


class DefensiveSpellAction(BaseModel):
    """A long-duration self-defense spell eligible for Iron Pit precombat preparation."""

    id: str
    name: str
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "action"
    duration_minutes: int = Field(ge=10)
    temporary_hp: int = Field(default=0, ge=0)
    temporary_hp_per_slot_above: int = Field(default=0, ge=0)
    damage_resistances: list[DamageTypeName] = Field(default_factory=list)
    concentration: bool = False
    priority: int = 0
    animation: str = "precombat-defense"

    @model_validator(mode="after")
    def validate_defense(self) -> "DefensiveSpellAction":
        if self.action_cost == "reaction":
            raise ValueError("Reaction spells cannot be pre-cast without their trigger.")
        if not self.temporary_hp and not self.damage_resistances:
            raise ValueError("Certified defensive spell must define an implemented defensive effect.")
        return self


class SpellSaveAction(BaseModel):
    """A spell whose certified combat resolution is a saving throw and optional damage."""

    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    area_radius_ft: int | None = Field(default=None, ge=5)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    success_damage: Literal["none", "half"] = "none"
    upcast_dice_per_level: int = Field(default=0, ge=0, le=20)
    concentration: bool = False
    animation: str = "spell-save"

    @model_validator(mode="after")
    def validate_spell(self) -> "SpellSaveAction":
        if self.area_radius_ft is not None and self.area_radius_ft % 5:
            raise ValueError("Iron Pit area spell radii must use 5-foot increments.")
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("Damaging spells require a damage type.")
        return self
