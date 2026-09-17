from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost, ConditionName, DamageTypeName

SpellModifierKind = Literal[
    "armor-class", "attack-roll-bonus-die", "saving-throw-bonus-die", "saving-throw-advantage",
    "death-save-advantage", "healing-maximize", "condition-immunity", "attacks-against-advantage",
    "attacks-against-disadvantage", "targeting-save-gate", "bonus-damage", "speed",
]
SpellTargetPolicy = Literal["self", "friendly"]
SpellAttackKind = Literal["melee", "ranged"]


class SpellModifierEffect(BaseModel):
    """Source-neutral modifier data converted to a runtime CombatModifier when a spell resolves."""

    kind: SpellModifierKind
    flat_bonus: int = 0
    dice_count: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(default=0, ge=0, le=100)
    damage_type: DamageTypeName | None = None
    condition_id: ConditionName | None = None
    source_creature_types: list[str] = Field(default_factory=list)
    save_ability: AbilityName | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    consume_on_attack_against: bool = False
    ends_on_owner_attack: bool = False
    expires_after_source_turns: int | None = Field(default=None, ge=1, le=20)

    @model_validator(mode="after")
    def validate_payload(self) -> "SpellModifierEffect":
        die_kind = self.kind in {"attack-roll-bonus-die", "saving-throw-bonus-die", "bonus-damage"}
        if die_kind and (self.dice_count < 1 or self.dice_size < 2):
            raise ValueError(f"{self.kind} requires certified dice.")
        if not die_kind and (self.dice_count or self.dice_size):
            raise ValueError(f"{self.kind} does not accept dice.")
        if self.kind == "bonus-damage" and self.damage_type is None:
            raise ValueError("Bonus damage requires a damage type.")
        if self.kind != "bonus-damage" and self.damage_type is not None:
            raise ValueError(f"{self.kind} does not accept a damage type.")
        if self.kind == "condition-immunity" and self.condition_id is None:
            raise ValueError("Condition immunity requires a condition id.")
        if self.kind != "condition-immunity" and self.condition_id is not None:
            raise ValueError(f"{self.kind} does not accept a condition id.")
        if self.kind == "attacks-against-disadvantage" and not self.source_creature_types:
            raise ValueError("Typed attack Disadvantage requires source creature types.")
        if self.source_creature_types and self.kind not in {"attacks-against-disadvantage", "condition-immunity"}:
            raise ValueError(f"{self.kind} does not accept source creature types.")
        if self.kind in {"saving-throw-advantage", "targeting-save-gate"} and not self.save_ability:
            raise ValueError(f"{self.kind} requires a save ability.")
        if self.kind == "targeting-save-gate" and self.save_dc is None:
            raise ValueError("Targeting save gates require a DC.")
        if self.kind != "targeting-save-gate" and self.save_dc is not None:
            raise ValueError(f"{self.kind} does not accept a save DC.")
        if self.kind not in {"saving-throw-advantage", "targeting-save-gate"} and self.save_ability:
            raise ValueError(f"{self.kind} does not accept a save ability.")
        if self.consume_on_attack_against and self.kind != "attacks-against-advantage":
            raise ValueError("Only attack-advantage spell modifiers can be consumed by the next attack.")
        if self.ends_on_owner_attack and self.kind != "targeting-save-gate":
            raise ValueError("Only targeting save gates can end when their owner attacks.")
        return self


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
