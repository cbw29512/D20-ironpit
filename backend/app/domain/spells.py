from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost, DamageTypeName, HealingTargetMode, HitControlEffect
from app.domain.modifiers import ModifierKind
from app.domain.targeting import AreaTargeting


class SpellModifierEffect(BaseModel):
    kind: ModifierKind
    flat_bonus: int = 0
    dice_count: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(default=6, ge=2, le=100)
    damage_type: DamageTypeName | None = None
    consume_on_attack_against: bool = False
    expires_at_start_of_source_turn: bool = False
    expires_after_source_turns: int | None = Field(default=None, ge=1, le=100)


class SpellAttackAction(BaseModel):
    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    attack_kind: Literal["melee", "ranged"] = "ranged"
    range_ft: int = Field(ge=0)
    attack_bonus: int
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    on_hit_modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    animation: str = "spell-attack"
    source: str | None = None


class SpellSaveAction(BaseModel):
    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    area_radius_ft: int | None = Field(default=None, ge=0)
    area: AreaTargeting | None = None
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    success_damage: Literal["none", "half"] = "none"
    upcast_dice_per_level: int = Field(default=0, ge=0, le=10)
    excluded_creature_types: list[str] = Field(default_factory=list)
    save_disadvantage_creature_types: list[str] = Field(default_factory=list)
    maximize_damage_creature_types: list[str] = Field(default_factory=list)
    concentration: bool = False
    animation: str = "spell-save"

    @model_validator(mode="after")
    def validate_area(self) -> "SpellSaveAction":
        if self.area is not None and self.area_radius_ft is not None:
            raise ValueError("Spell save action cannot define both legacy radius and structured area targeting.")
        return self


class DefensiveSpellAction(BaseModel):
    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(default=0, ge=0)
    duration_minutes: int = Field(default=1, ge=1, le=1440)
    target_policy: Literal["self", "self_or_ally"] = "self"
    target_count: int = Field(default=1, ge=1, le=20)
    temporary_hp: int = Field(default=0, ge=0)
    temporary_hp_per_slot_above: int = Field(default=0, ge=0)
    damage_resistances: list[DamageTypeName] = Field(default_factory=list)
    modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    max_hp_increase: int = Field(default=0, ge=0)
    current_hp_increase: int = Field(default=0, ge=0)
    concentration: bool = False
    priority: int = 0
    animation: str = "defensive-spell"
    source: str | None = None


class HealingSpellAction(BaseModel):
    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(default=5, ge=0)
    target_mode: HealingTargetMode = "self_or_ally"
    dice_count: int = Field(default=0, ge=0, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    healing_bonus: int = Field(default=0, ge=0)
    upcast_dice_per_level: int = Field(default=0, ge=0, le=10)
    source: str | None = None
    animation: str = "healing-spell"


class SpellControlAction(BaseModel):
    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(default=60, ge=0)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    failure_control_effect: HitControlEffect
    concentration: bool = True
    animation: str = "spell-control"


class SpellSlotProfile(BaseModel):
    level: int = Field(ge=1, le=9)
    max_uses: int = Field(ge=0, le=20)
