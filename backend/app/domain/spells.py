from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost, DamageTypeName

from app.domain.spell_modifiers import SpellModifierEffect, SpellModifierKind

SpellTargetPolicy = Literal["self", "friendly"]
SpellAttackKind = Literal["melee", "ranged"]


class DefensiveSpellAction(BaseModel):
    """A certified precombat defensive/buff spell with deterministic arena targeting."""

    id: str
    name: str
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(default=0, ge=0)
    duration_minutes: int = Field(ge=1)
    target_policy: SpellTargetPolicy = "self"
    target_count: int = Field(default=1, ge=1, le=20)
    target_count_per_slot_above: int = Field(default=0, ge=0, le=20)
    temporary_hp: int = Field(default=0, ge=0)
    temporary_hp_per_slot_above: int = Field(default=0, ge=0)
    max_hp_increase: int = Field(default=0, ge=0)
    current_hp_increase: int = Field(default=0, ge=0)
    damage_resistances: list[DamageTypeName] = Field(default_factory=list)
    modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    concentration: bool = False
    priority: int = 0
    animation: str = "precombat-defense"
    source: str | None = None

    @model_validator(mode="after")
    def validate_defense(self) -> "DefensiveSpellAction":
        direct_hp = self.temporary_hp or self.max_hp_increase or self.current_hp_increase
        if not direct_hp and not self.damage_resistances and not self.modifier_effects:
            raise ValueError("Certified defensive spell must define an implemented defensive effect.")
        if self.concentration and (direct_hp or self.damage_resistances):
            raise ValueError("Concentration defenses require source-owned modifier effects.")
        if self.target_policy == "self" and (self.target_count != 1 or self.target_count_per_slot_above):
            raise ValueError("Self-target policy supports exactly one target.")
        return self


class SpellAttackAction(BaseModel):
    """A spell resolved with an attack roll rather than a saving throw."""

    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    attack_kind: SpellAttackKind = "ranged"
    range_ft: int = Field(ge=0)
    attack_bonus: int
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    on_hit_modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    animation: str = "spell-attack"
    source: str | None = None

    @model_validator(mode="after")
    def validate_attack_spell(self) -> "SpellAttackAction":
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("Damaging spell attacks require a damage type.")
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
