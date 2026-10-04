from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost, ConditionName
from app.domain.hit_effects import OnHitTimedEffect
from app.domain.movement import MovementModeGrant
from app.domain.save_damage import DamageTypeName, SaveDamageComponent
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

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
    target_all_legal: bool = False
    target_count_per_slot_above: int = Field(default=0, ge=0, le=20)
    temporary_hp: int = Field(default=0, ge=0)
    temporary_hp_per_slot_above: int = Field(default=0, ge=0)
    max_hp_increase: int = Field(default=0, ge=0)
    current_hp_increase: int = Field(default=0, ge=0)
    damage_resistances: list[DamageTypeName] = Field(default_factory=list)
    selectable_resistance_types: list[DamageTypeName] = Field(default_factory=list)
    share_damage_with_source: bool = False
    share_range_ft: int = Field(default=0, ge=0)
    condition_ids: list[ConditionName] = Field(default_factory=list)
    modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    movement_mode_grants: list[MovementModeGrant] = Field(default_factory=list)
    concentration: bool = False
    free_opening_cast: bool = False
    priority: int = 0
    animation: str = "precombat-defense"
    source: str | None = None

    @model_validator(mode="after")
    def validate_defense(self) -> "DefensiveSpellAction":
        direct_hp = self.temporary_hp or self.max_hp_increase or self.current_hp_increase
        if not (
            direct_hp or self.damage_resistances or self.selectable_resistance_types
            or self.share_damage_with_source or self.condition_ids
            or self.modifier_effects or self.movement_mode_grants
        ):
            raise ValueError("Certified defensive spell must define an implemented defensive effect.")
        if self.concentration and direct_hp:
            raise ValueError("Concentration defenses require source-owned modifier or timed-condition effects.")
        if self.share_damage_with_source and self.share_range_ft <= 0:
            raise ValueError("Damage-share wards require a positive share range.")
        if self.target_policy == "self" and (
            self.target_count != 1 or self.target_all_legal or self.target_count_per_slot_above
        ):
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
    attack_count: int = Field(default=1, ge=1, le=20)
    attacks_per_slot_above: int = Field(default=0, ge=0, le=20)
    upcast_dice_per_level: int = Field(default=0, ge=0, le=20)
    advantage_if_target_wearing_metal_armor: bool = False
    on_hit_modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    on_hit_timed_effects: list[OnHitTimedEffect] = Field(default_factory=list)
    miss_damage: Literal["none", "half"] = "none"
    matching_dice_leap_range_ft: int = Field(default=0, ge=0)
    animation: str = "spell-attack"
    source: str | None = None

    @model_validator(mode="after")
    def validate_attack_spell(self) -> "SpellAttackAction":
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("Damaging spell attacks require a damage type.")
        if self.level == 0 and (self.attacks_per_slot_above or self.upcast_dice_per_level):
            raise ValueError("Cantrip spell attacks cannot scale by spell-slot level.")
        if self.matching_dice_leap_range_ft:
            if self.matching_dice_leap_range_ft % 5:
                raise ValueError("Matching-dice leap range must use 5-foot increments.")
            if self.attack_count > 1 or self.attacks_per_slot_above:
                raise ValueError("Matching-dice leap requires a single-attack spell.")
            if not self.damage_dice_count:
                raise ValueError("Matching-dice leap requires damage dice.")
        return self

    def attack_count_at_slot(self, slot_level: int) -> int:
        if self.level == 0:
            if slot_level != 0:
                raise ValueError("Cantrip spell attacks use slot level 0.")
            return self.attack_count
        if slot_level < self.level or slot_level > 9:
            raise ValueError(f"Illegal slot level {slot_level} for {self.name}.")
        return self.attack_count + (slot_level - self.level) * self.attacks_per_slot_above

    def damage_dice_at_slot(self, slot_level: int) -> int:
        if self.level == 0:
            return self.damage_dice_count
        if slot_level < self.level or slot_level > 9:
            raise ValueError(f"Illegal slot level {slot_level} for {self.name}.")
        return self.damage_dice_count + (slot_level - self.level) * self.upcast_dice_per_level


class SpellSaveAction(BaseModel):
    """A spell whose certified combat resolution is a saving throw and optional damage."""

    id: str
    name: str
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    area_radius_ft: int | None = Field(default=None, ge=5)
    area: AreaTargeting | None = None
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    success_damage: Literal["none", "half"] = "none"
    damage_components: list[SaveDamageComponent] = Field(default_factory=list)
    upcast_dice_per_level: int = Field(default=0, ge=0, le=20)
    effect_tags: list[str] = Field(default_factory=list)
    automatic_failure_creature_types: list[str] = Field(default_factory=list)
    requires_target_hearing: bool = False
    requires_target_sight: bool = False
    failed_save_timed_effect: FailedSaveTimedEffect | None = None
    failed_save_push_ft: int = Field(default=0, ge=0)
    failed_save_modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    required_target_creature_types: list[str] = Field(default_factory=list)
    excluded_target_creature_types: list[str] = Field(default_factory=list)
    minimum_remaining_hp: int = Field(default=0, ge=0)
    reduce_hit_point_maximum_on_failed_save: bool = False
    verbal_component: bool = True
    concentration: bool = False
    repeat_only: bool = False
    duration_minutes: int | None = Field(default=None, ge=1)
    allows_higher_slots: bool = False
    target_count: int = Field(default=1, ge=1, le=20)
    target_count_per_slot_above: int = Field(default=0, ge=0, le=20)
    save_advantage_if_fighting: bool = False
    cast_rounds: int = Field(default=1, ge=1, le=100)
    creates_difficult_terrain: bool = False
    difficult_terrain_duration_rounds: int = Field(default=0, ge=0, le=100)
    animation: str = "spell-save"

    @model_validator(mode="after")
    def validate_spell(self) -> "SpellSaveAction":
        if self.area_radius_ft is not None and self.area_radius_ft % 5:
            raise ValueError("Iron Pit area spell radii must use 5-foot increments.")
        if self.area_radius_ft is not None and self.area is not None:
            raise ValueError("Save spells must use either legacy radius geometry or universal area geometry, not both.")
        if self.concentration and self.duration_minutes is None:
            raise ValueError("Concentration save spells require a certified duration.")
        if self.damage_components and (self.damage_dice_count or self.damage_type is not None or self.damage_bonus):
            raise ValueError("Multi-component save spells cannot also define legacy single-component damage.")
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("Damaging spells require a damage type.")
        if self.creates_difficult_terrain and self.difficult_terrain_duration_rounds < 1:
            raise ValueError("Difficult-terrain save spells require a positive duration.")
        return self
