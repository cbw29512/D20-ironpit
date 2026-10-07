from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ConditionName, ConditionRemovalAction, HealingAction
from app.domain.area_weapon_attacks import AreaWeaponAttackAction
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.capability_attacks import (
    AttackCapabilityDefinition,
    CapabilityActionSlot,
    MultiattackCapabilityDefinition,
    SaveCapabilityDefinition,
)
from app.domain.character_builds import AbilityScores
from app.domain.combatants import ResourceDefinition, VisualLoadout
from app.domain.damage_sources import ConditionalDamageDefense
from app.domain.damage_absorption import DamageAbsorptionRule
from app.domain.tactical_actions import BonusActionTacticalGrant
from app.domain.effect_removal import EffectRemovalAction, EffectTagConditionGrant
from app.domain.environment_contexts import EnvironmentContextReaction
from app.domain.movement import MovementModes
from app.domain.progression import ProgressionCombatFeatures
from app.domain.recharge import RechargeRule
from app.domain.regeneration import RegenerationTrait
from app.domain.save_success_overrides import FailedSaveSuccessOverride
from app.domain.reactions import ParryReaction, RedirectAttackReaction
from app.domain.rulesets import RulesetId
from app.domain.size import CreatureSize
from app.domain.legendary_actions import LegendaryActionOption
from app.domain.spells import DefensiveSpellAction, SpellSaveAction
from app.domain.timed_self_buffs import TimedSelfBuffAction
from app.domain.triggered_extra_attacks import TriggeredExtraAttackStack
from app.domain.traits import CombatTrait
from app.domain.zero_hp_effects import DamageThresholdZeroHpReplacement
from app.domain.unarmed import UnarmedStrikeDamage
from app.domain.weapons import DamageType


class CombatantDefinition(BaseModel):
    schema_version: Literal[1] = 1
    id: str
    name: str
    archetype: str
    level: int | None = Field(default=None, ge=1, le=20)
    challenge_rating: str | None = None
    kind: Literal["character", "monster"]
    ruleset: RulesetId
    creature_type: str | None = None
    size: CreatureSize = CreatureSize.MEDIUM
    ability_scores: AbilityScores | None = None
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    speed_ft: int = Field(ge=0)
    movement_modes: MovementModes | None = None
    initiative_bonus: int
    blindsight_ft: int = Field(default=0, ge=0)
    truesight_ft: int = Field(default=0, ge=0)
    progression_features: ProgressionCombatFeatures = Field(default_factory=ProgressionCombatFeatures)
    environment_context_reactions: list[EnvironmentContextReaction] = Field(default_factory=list)
    bonus_attack_grants: list[BonusAttackGrant] = Field(default_factory=list)
    bonus_tactical_action_grants: list[BonusActionTacticalGrant] = Field(default_factory=list)
    attacks: list[AttackCapabilityDefinition] = Field(min_length=1)
    primary_attack_id: str
    unarmed_opportunity_attack: UnarmedStrikeDamage | None = None
    attack_action: MultiattackCapabilityDefinition | None = None
    area_weapon_attack_actions: list[AreaWeaponAttackAction] = Field(default_factory=list)
    save_actions: list[SaveCapabilityDefinition] = Field(default_factory=list)
    spell_save_actions: list[SpellSaveAction] = Field(default_factory=list)
    defensive_spell_actions: list[DefensiveSpellAction] = Field(default_factory=list)
    healing_actions: list[HealingAction] = Field(default_factory=list)
    timed_self_buff_actions: list[TimedSelfBuffAction] = Field(default_factory=list)
    legendary_actions: list[LegendaryActionOption] = Field(default_factory=list)
    condition_removal_actions: list[ConditionRemovalAction] = Field(default_factory=list)
    effect_removal_actions: list[EffectRemovalAction] = Field(default_factory=list)
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
    fighting_styles: list[str] = Field(default_factory=list)
    weapon_masteries: list[str] = Field(default_factory=list)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)
    damage_absorptions: list[DamageAbsorptionRule] = Field(default_factory=list)
    conditional_damage_defenses: list[ConditionalDamageDefense] = Field(default_factory=list)
    condition_immunities: list[ConditionName] = Field(default_factory=list)
    terminal_effect_tags: list[str] = Field(default_factory=list)
    effect_tag_condition_grants: list[EffectTagConditionGrant] = Field(default_factory=list)
    wearing_heavy_armor: bool = False
    wearing_metal_armor: bool = False
    rage_damage_bonus: int = Field(default=0, ge=0, le=10)
    resources: list[ResourceDefinition] = Field(default_factory=list)
    recharge_rules: list[RechargeRule] = Field(default_factory=list)
    regeneration: RegenerationTrait | None = None
    damage_threshold_zero_hp_replacements: list[DamageThresholdZeroHpReplacement] = Field(default_factory=list)
    triggered_extra_attack_stacks: list[TriggeredExtraAttackStack] = Field(default_factory=list)
    save_success_overrides: list[FailedSaveSuccessOverride] = Field(default_factory=list)
    visual: VisualLoadout
    source: str
    unsupported_capabilities: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_fighting_styles(cls, values: object) -> object:
        if not isinstance(values, dict):
            return values
        normalized = dict(values)
        style = normalized.get("fighting_style")
        styles = normalized.get("fighting_styles") or []
        if not styles and style:
            normalized["fighting_styles"] = [style]
        elif styles and not style:
            normalized["fighting_style"] = styles[0]
        return normalized

    @model_validator(mode="after")
    def validate_references(self) -> "CombatantDefinition":
        attack_ids = {attack.id for attack in self.attacks}
        save_ids = {action.id for action in self.save_actions}
        if self.kind == "character" and self.ability_scores is None:
            raise ValueError("Character combatant definitions require ability scores.")
        if len(attack_ids) != len(self.attacks) or len(save_ids) != len(self.save_actions):
            raise ValueError("Capability ids must be unique within their action family.")
        if self.primary_attack_id not in attack_ids:
            raise ValueError("primary_attack_id must reference a declared attack.")
        if self.attack_action:
            for slot in self.attack_action.slots:
                if not set(slot.attack_ids) <= attack_ids or not set(slot.save_action_ids) <= save_ids:
                    raise ValueError("Multiattack slot references an undeclared capability id.")
        if any(action.attack_id not in attack_ids for action in self.area_weapon_attack_actions):
            raise ValueError("Area weapon attack references an undeclared attack capability id.")
        return self
