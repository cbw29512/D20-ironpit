from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionRemovalAction, HealingAction
from app.domain.capability_effects import AttackEffectDefinition, DiceSpec, GrappleEffectDefinition
from app.domain.combatants import DamageType, ResourceDefinition, VisualLoadout, WeaponAttackKind
from app.domain.movement import MovementModes
from app.domain.progression import ProgressionCombatFeatures
from app.domain.reactions import ParryReaction, RedirectAttackReaction
from app.domain.size import CreatureSize
from app.domain.spells import DefensiveSpellAction, SpellSaveAction
from app.domain.traits import CombatTrait
from app.domain.unarmed import UnarmedStrikeDamage


class AttackCapabilityDefinition(BaseModel):
    id: str
    name: str
    weapon_id: str | None = None
    attack_kind: WeaponAttackKind
    attack_bonus: int
    damage: DiceSpec | None = None
    fixed_damage: int | None = Field(default=None, ge=0)
    damage_type: DamageType
    animation: str
    reach_ft: int = Field(default=5, ge=0)
    normal_range_ft: int | None = Field(default=None, ge=1)
    long_range_ft: int | None = Field(default=None, ge=1)
    projectile: str | None = None
    mastery_property: str | None = None
    light: bool = False
    attack_ability: AbilityName | None = None
    attack_ability_modifier: int | None = None
    rage_eligible: bool = False
    effects: list[AttackEffectDefinition] = Field(default_factory=list)
    forbid_target_grappled_by_self: bool = False

    @model_validator(mode="after")
    def validate_attack_shape(self) -> "AttackCapabilityDefinition":
        if (self.damage is None) == (self.fixed_damage is None):
            raise ValueError("Attack must declare exactly one of damage or fixed_damage.")
        if self.attack_kind == WeaponAttackKind.RANGED and (
            self.normal_range_ft is None or self.long_range_ft is None
        ):
            raise ValueError("Ranged attack requires normal and long range.")
        if self.attack_ability_modifier is not None and self.attack_ability is None:
            raise ValueError("Attack ability modifier requires an explicit attack ability.")
        control_count = sum(effect.kind in {"grapple", "condition"} for effect in self.effects)
        if control_count > 1:
            raise ValueError("Current runtime supports one persistent control rider per attack.")
        return self

class SaveCapabilityDefinition(BaseModel):
    id: str
    name: str
    save_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    dc: int = Field(ge=1, le=40)
    range_ft: int = Field(ge=0)
    target_max_size: CreatureSize | None = None
    damage: DiceSpec | None = None
    damage_type: DamageType | None = None
    success_damage: Literal["none", "half"] = "none"
    grapple: GrappleEffectDefinition | None = None
    animation: str = "save-effect"

    @model_validator(mode="after")
    def validate_damage(self) -> "SaveCapabilityDefinition":
        if (self.damage is None) != (self.damage_type is None):
            raise ValueError("Save damage dice and damage type must be declared together.")
        if self.grapple and self.grapple.max_target_size and self.target_max_size:
            if self.grapple.max_target_size != self.target_max_size:
                raise ValueError("Save target size and grapple target size cannot disagree.")
        return self

class CapabilityActionSlot(BaseModel):
    attack_ids: list[str] = Field(default_factory=list, max_length=16)
    save_action_ids: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def require_choice(self) -> "CapabilityActionSlot":
        if not self.attack_ids and not self.save_action_ids:
            raise ValueError("Attack-action slot requires an attack or save action.")
        return self

class MultiattackCapabilityDefinition(BaseModel):
    id: str
    name: str = "Multiattack"
    is_attack_action: bool = False
    slots: list[CapabilityActionSlot] = Field(min_length=1, max_length=8)


class CombatantDefinition(BaseModel):
    schema_version: Literal[1] = 1
    id: str
    name: str
    archetype: str
    level: int | None = Field(default=None, ge=1, le=20)
    challenge_rating: str | None = None
    kind: Literal["character", "monster"]
    size: CreatureSize = CreatureSize.MEDIUM
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    speed_ft: int = Field(ge=0)
    movement_modes: MovementModes | None = None
    initiative_bonus: int
    progression_features: ProgressionCombatFeatures = Field(default_factory=ProgressionCombatFeatures)
    attacks: list[AttackCapabilityDefinition] = Field(min_length=1)
    primary_attack_id: str
    unarmed_opportunity_attack: UnarmedStrikeDamage | None = None
    attack_action: MultiattackCapabilityDefinition | None = None
    save_actions: list[SaveCapabilityDefinition] = Field(default_factory=list)
    spell_save_actions: list[SpellSaveAction] = Field(default_factory=list)
    defensive_spell_actions: list[DefensiveSpellAction] = Field(default_factory=list)
    healing_actions: list[HealingAction] = Field(default_factory=list)
    condition_removal_actions: list[ConditionRemovalAction] = Field(default_factory=list)
    saving_throw_bonuses: dict[str, int] = Field(default_factory=dict)
    skill_bonuses: dict[str, int] = Field(default_factory=dict)
    combat_traits: list[CombatTrait] = Field(default_factory=list)
    source_trait_names: list[str] = Field(default_factory=list)
    source_reaction_names: list[str] = Field(default_factory=list)
    source_bonus_action_names: list[str] = Field(default_factory=list)
    source_limited_use_names: list[str] = Field(default_factory=list)
    source_legendary_action_names: list[str] = Field(default_factory=list)
    source_spellcasting_fingerprint: str | None = None
    parry_reaction: ParryReaction | None = None
    redirect_attack_reaction: RedirectAttackReaction | None = None
    fighting_style: str | None = None
    weapon_masteries: list[str] = Field(default_factory=list)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)
    condition_immunities: list[ConditionName] = Field(default_factory=list)
    wearing_heavy_armor: bool = False
    rage_damage_bonus: int = Field(default=0, ge=0, le=10)
    resources: list[ResourceDefinition] = Field(default_factory=list)
    visual: VisualLoadout
    source: str
    unsupported_capabilities: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> "CombatantDefinition":
        attack_ids = {attack.id for attack in self.attacks}
        save_ids = {action.id for action in self.save_actions}
        if len(attack_ids) != len(self.attacks) or len(save_ids) != len(self.save_actions):
            raise ValueError("Capability ids must be unique within their action family.")
        if self.primary_attack_id not in attack_ids:
            raise ValueError("primary_attack_id must reference a declared attack.")
        if self.attack_action:
            for slot in self.attack_action.slots:
                if not set(slot.attack_ids) <= attack_ids or not set(slot.save_action_ids) <= save_ids:
                    raise ValueError("Multiattack slot references an undeclared capability id.")
        return self