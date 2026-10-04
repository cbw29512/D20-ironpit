from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AttackActionDefinition, ConditionName, ConditionRemovalAction, HealingAction, HpThresholdConditionAction, HpThresholdInstantDeathAction, SavingThrowAction
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.area_weapon_attacks import AreaWeaponAttackAction
from app.domain.attack_action_weapon_buffs import AttackActionWeaponBuff
from app.domain.character_builds import AbilityScores
from app.domain.damage_sources import ConditionalDamageDefense
from app.domain.effect_removal import EffectRemovalAction
from app.domain.d20_bonus_dice import D20BonusDieAction
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.movement import MovementModes
from app.domain.passive_modifiers import PassiveModifierGrant
from app.domain.persistent_barriers import PersistentBarrierAction
from app.domain.persistent_beneficial_zones import PersistentBeneficialZoneAction
from app.domain.persistent_hazards import PersistentHazardAction
from app.domain.persistent_save_zones import PersistentSaveZoneAction
from app.domain.suppression_zones import PersistentSuppressionZoneAction
from app.domain.teleport_actions import TeleportAction
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction
from app.domain.progression import ProgressionCombatFeatures
from app.domain.reactions import AttackDamageReductionReaction, DamageReactionAttack, ParryReaction, RedirectAttackReaction
from app.domain.reaction_roll_penalties import ReactionRollPenaltyAction
from app.domain.concentration_repeat_saves import ConcentrationRepeatSaveAction
from app.domain.recharge import RechargeRule
from app.domain.replacement_form_actions import ReplacementFormAction
from app.domain.resource_conversion import ResourceConversionAction
from app.domain.rulesets import DEFAULT_RULESET, RulesetId
from app.domain.size import CreatureSize
from app.domain.spell_cast_modifiers import ResourceBackedSpellDurationModifier, ResourceBackedSpellRangeModifier, ResourceBackedSpellSaveDisadvantage
from app.domain.spell_cast_effects import SpellCastTimedResistance
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellSaveAction
from app.domain.timed_self_buffs import TimedSelfBuffAction
from app.domain.targeted_concentration_damage import TargetedConcentrationDamageAction
from app.domain.tactical_actions import BonusActionTacticalGrant
from app.domain.traits import CombatTrait
from app.domain.unarmed import UnarmedStrikeDamage
from app.domain.weapons import (
    ConditionalAttackAdvantage,
    ConditionalDamage,
    DamageType,
    OnHitDamage,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)


class VisualLoadout(BaseModel):
    armor: str
    main_hand: str
    off_hand: str | None = None
    body_style: str = "humanoid"


class ResourceDefinition(BaseModel):
    id: str
    name: str
    max_uses: int = Field(ge=0)


class CombatantTemplate(BaseModel):
    id: str
    name: str
    archetype: str
    level: int | None = Field(default=None, ge=1, le=20)
    challenge_rating: str | None = None
    kind: Literal["character", "monster"]
    ruleset: RulesetId = DEFAULT_RULESET
    creature_type: str | None = None
    size: CreatureSize = CreatureSize.MEDIUM
    ability_scores: AbilityScores | None = None
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    speed_ft: int = Field(ge=0)
    movement_modes: MovementModes
    initiative_bonus: int
    starts_with_heroic_inspiration: bool = False
    blindsight_ft: int = Field(default=0, ge=0)
    truesight_ft: int = Field(default=0, ge=0)
    progression_features: ProgressionCombatFeatures = Field(default_factory=ProgressionCombatFeatures)
    passive_modifier_grants: list[PassiveModifierGrant] = Field(default_factory=list)
    weapon_attack: WeaponAttack
    alternate_weapon_attacks: list[WeaponAttack] = Field(default_factory=list)
    unarmed_opportunity_attack: UnarmedStrikeDamage | None = None
    attack_action: AttackActionDefinition | None = None
    attack_action_weapon_buffs: list[AttackActionWeaponBuff] = Field(default_factory=list)
    bonus_attack_grants: list[BonusAttackGrant] = Field(default_factory=list)
    bonus_tactical_action_grants: list[BonusActionTacticalGrant] = Field(default_factory=list)
    area_weapon_attack_actions: list[AreaWeaponAttackAction] = Field(default_factory=list)
    saving_throw_actions: list[SavingThrowAction] = Field(default_factory=list)
    hp_threshold_condition_actions: list[HpThresholdConditionAction] = Field(default_factory=list)
    hp_threshold_instant_death_actions: list[HpThresholdInstantDeathAction] = Field(default_factory=list)
    spell_save_actions: list[SpellSaveAction] = Field(default_factory=list)
    spell_attack_actions: list[SpellAttackAction] = Field(default_factory=list)
    auto_hit_spell_actions: list[AutoHitSpellAction] = Field(default_factory=list)
    spell_cast_timed_resistances: list[SpellCastTimedResistance] = Field(default_factory=list)
    persistent_spell_attack_actions: list[PersistentSpellAttackAction] = Field(default_factory=list)
    persistent_hazard_actions: list[PersistentHazardAction] = Field(default_factory=list)
    persistent_barrier_actions: list[PersistentBarrierAction] = Field(default_factory=list)
    persistent_beneficial_zone_actions: list[PersistentBeneficialZoneAction] = Field(default_factory=list)
    suppression_zone_actions: list[PersistentSuppressionZoneAction] = Field(default_factory=list)
    persistent_save_zone_actions: list[PersistentSaveZoneAction] = Field(default_factory=list)
    teleport_actions: list[TeleportAction] = Field(default_factory=list)
    defensive_spell_actions: list[DefensiveSpellAction] = Field(default_factory=list)
    healing_actions: list[HealingAction] = Field(default_factory=list)
    d20_bonus_die_actions: list[D20BonusDieAction] = Field(default_factory=list)
    condition_removal_actions: list[ConditionRemovalAction] = Field(default_factory=list)
    initiative_resource_refill_grants: list[InitiativeResourceRefillGrant] = Field(default_factory=list)
    resource_conversion_actions: list[ResourceConversionAction] = Field(default_factory=list)
    spell_save_disadvantage_options: list[ResourceBackedSpellSaveDisadvantage] = Field(default_factory=list)
    spell_range_modifiers: list[ResourceBackedSpellRangeModifier] = Field(default_factory=list)
    spell_duration_modifiers: list[ResourceBackedSpellDurationModifier] = Field(default_factory=list)
    timed_self_buff_actions: list[TimedSelfBuffAction] = Field(default_factory=list)
    targeted_concentration_damage_actions: list[TargetedConcentrationDamageAction] = Field(default_factory=list)
    replacement_form_actions: list[ReplacementFormAction] = Field(default_factory=list)
    concentration_repeat_save_actions: list[ConcentrationRepeatSaveAction] = Field(default_factory=list)
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
    attack_damage_reduction_reaction: AttackDamageReductionReaction | None = None
    parry_reaction: ParryReaction | None = None
    redirect_attack_reaction: RedirectAttackReaction | None = None
    damage_reaction_attack: DamageReactionAttack | None = None
    reaction_roll_penalty_actions: list[ReactionRollPenaltyAction] = Field(default_factory=list)
    fighting_style: str | None = None
    fighting_styles: list[str] = Field(default_factory=list)
    weapon_masteries: list[str] = Field(default_factory=list)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)
    conditional_damage_defenses: list[ConditionalDamageDefense] = Field(default_factory=list)
    condition_immunities: list[ConditionName] = Field(default_factory=list)
    wearing_heavy_armor: bool = False
    wearing_metal_armor: bool = False
    rage_damage_bonus: int = Field(default=0, ge=0, le=10)
    visual: VisualLoadout
    resources: list[ResourceDefinition] = Field(default_factory=list)
    unlimited_resource_ids: list[str] = Field(default_factory=list)
    recharge_rules: list[RechargeRule] = Field(default_factory=list)
    source: str

    @model_validator(mode="before")
    @classmethod
    def _normalize_compatibility_fields(cls, values: object) -> object:
        if not isinstance(values, dict):
            return values
        normalized = dict(values)
        if "movement_modes" not in normalized and "speed_ft" in normalized:
            normalized["movement_modes"] = {"walk_ft": normalized["speed_ft"]}
        style = normalized.get("fighting_style")
        styles = normalized.get("fighting_styles")
        if styles is None:
            styles = []
        if not styles and style:
            normalized["fighting_styles"] = [style]
        elif styles and not style:
            normalized["fighting_style"] = styles[0]
        unlimited = set(normalized.get("unlimited_resource_ids") or [])
        finite_ids = {
            getattr(item, "id", None) if not isinstance(item, dict) else item.get("id")
            for item in (normalized.get("resources") or [])
        }
        overlap = sorted(item for item in unlimited.intersection(finite_ids) if item)
        if overlap:
            raise ValueError(f"Resources cannot be both finite and unlimited: {overlap}.")
        return normalized
