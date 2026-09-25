from __future__ import annotations

from pydantic import BaseModel, Field, model_validator
from typing import Literal

from app.domain.character_builds import AbilityName
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.healing_riders import OutgoingHealingDiceMaximizer


class AbilityCheckMinimum(BaseModel):
    """Declarative floor for one ability-check family; resolution remains name-agnostic."""

    source_id: str
    ability: AbilityName
    minimum_source: Literal["ability_score"] = "ability_score"


class AbilityScaledDamageRider(BaseModel):
    """Damage dice count derived from one ability modifier."""

    source_id: str
    ability: AbilityName
    dice_size: int = Field(ge=2, le=100)
    damage_type: str


class SlotHealingSelfRider(BaseModel):
    """Heal the source after a slotted healing spell restores HP to another creature."""

    source_id: str
    flat_bonus: int = Field(default=0, ge=0)
    per_slot_level: int = Field(default=0, ge=0)


class EffectBoundSurvivalSave(BaseModel):
    """Immutable zero-HP replacement parameters; no class identity enters resolution."""

    source_id: str
    required_effect_id: str
    save_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"] = "constitution"
    initial_dc: int = Field(ge=1)
    dc_increment: int = Field(default=0, ge=0)
    replacement_hp: int = Field(ge=1)


class FirstRoundExtraTurnGrant(BaseModel):
    """Source-tagged extra first-round turn at an initiative offset."""

    source_id: str
    source_name: str
    initiative_offset: int = Field(ge=-30, le=30)


class OpeningTargetingWard(BaseModel):
    """Passive targeting-save gate installed when combat state is created."""

    source_id: str
    save_ability: AbilityName = "wisdom"
    save_dc: int = Field(ge=1, le=40)
    ends_on_owner_attack: bool = True


class SavingThrowProficiencyGrant(BaseModel):
    """Source-tagged saving throw proficiencies granted by progression data."""

    source_id: str
    abilities: list[AbilityName] = Field(min_length=1)


class SavingThrowAdvantageGrant(BaseModel):
    """Passive source-tagged Advantage on matching saving throws."""

    source_id: str
    source_name: str = Field(min_length=1)
    abilities: list[AbilityName] = Field(min_length=1)
    requires_magical_effect: bool = False
    requires_spell_effect: bool = False
    source_creature_types: list[str] = Field(default_factory=list)
    required_effect_tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_abilities(self) -> "SavingThrowAdvantageGrant":
        if len(set(self.abilities)) != len(self.abilities):
            raise ValueError("Saving-throw Advantage abilities must be unique.")
        normalized = [item.strip().casefold() for item in self.source_creature_types]
        if any(not item for item in normalized):
            raise ValueError("Saving-throw Advantage source creature types must be non-empty.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Saving-throw Advantage source creature types must be unique.")
        effect_tags = [item.strip().casefold() for item in self.required_effect_tags]
        if any(not item for item in effect_tags):
            raise ValueError("Saving-throw Advantage effect tags must be non-empty.")
        if len(set(effect_tags)) != len(effect_tags):
            raise ValueError("Saving-throw Advantage effect tags must be unique.")
        self.source_creature_types = normalized
        self.required_effect_tags = effect_tags
        return self


class FailedSaveRerollGrant(BaseModel):
    """Source-tagged, resource-backed reroll of a failed saving throw."""

    source_id: str
    source_name: str
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)


class FailedD20TestOverrideGrant(BaseModel):
    """Resource-backed replacement of a failed eligible D20 Test roll."""

    source_id: str
    source_name: str
    resource_id: str
    replacement_roll: int = Field(default=20, ge=1, le=20)
    test_kinds: list[Literal["attack", "saving_throw", "ability_check"]] = Field(min_length=1)


class DeferredSaveEffect(BaseModel):
    """Hit-armed effect later resolved by a generic Action and saving throw."""

    source_id: str
    source_name: str
    trigger_weapon_ids: list[str] = Field(min_length=1)
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)
    save_ability: AbilityName
    save_dc: int = Field(ge=1, le=40)
    failure_sets_zero_hp: bool = False
    success_damage_dice_count: int = Field(default=0, ge=0, le=40)
    success_damage_dice_size: int = Field(default=10, ge=2, le=100)
    success_damage_type: str | None = None
    max_active_targets: int = Field(default=1, ge=1, le=20)


class ProgressionCombatFeatures(BaseModel):
    """Level/subclass combat flags that should stay out of core stat-block shape."""

    effect_bound_survival_save: EffectBoundSurvivalSave | None = None
    turning_failure_damage: AbilityScaledDamageRider | None = None
    turning_failure_destroy_max_cr: str | None = None
    slot_healing_other_self_rider: SlotHealingSelfRider | None = None
    outgoing_healing_dice_maximizer: OutgoingHealingDiceMaximizer | None = None
    once_per_turn_weapon_hit_damage_rider: OncePerTurnWeaponHitDamageRider | None = None
    ability_check_minimums: list[AbilityCheckMinimum] = Field(default_factory=list)
    saving_throw_proficiency_grants: list[SavingThrowProficiencyGrant] = Field(default_factory=list)
    saving_throw_advantage_grants: list[SavingThrowAdvantageGrant] = Field(default_factory=list)
    opening_targeting_ward: OpeningTargetingWard | None = None
    first_round_extra_turn_grants: list[FirstRoundExtraTurnGrant] = Field(default_factory=list)
    failed_save_reroll_grants: list[FailedSaveRerollGrant] = Field(default_factory=list)
    failed_d20_test_override_grants: list[FailedD20TestOverrideGrant] = Field(default_factory=list)
    deferred_save_effect: DeferredSaveEffect | None = None
    critical_hit_minimum: int = Field(default=20, ge=2, le=20)
    initiative_advantage: bool = False
    first_round_extra_turn_initiative_offset: int | None = Field(default=None, ge=-30, le=30)
    suppress_attack_advantage_while_not_incapacitated: bool = False
    miss_to_hit_override_resource_id: str | None = None
    miss_to_hit_override_source_name: str | None = None
    athletics_advantage: bool = False
    danger_sense: bool = False
    reckless_attack: bool = False
    frenzy: bool = False
    frenzy_bonus_attack_2014: bool = False
    persistent_rage_2014: bool = False
    intimidating_presence_2014_dc: int = Field(default=0, ge=0, le=40)
    brutal_critical_dice: int = Field(default=0, ge=0, le=3)
    fast_movement_bonus_ft: int = Field(default=0, ge=0)
    mindless_rage: bool = False
    instinctive_pounce_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    brutal_strike_damage_dice: int = Field(default=0, ge=0, le=2)
    great_weapon_fighting: bool = False
    indomitable_reroll: bool = False
    indomitable_bonus: int = Field(default=0, ge=0, le=20)
    tactical_master_sap_weapon_ids: list[str] = Field(default_factory=list)
    heroic_warrior: bool = False
    studied_attacks: bool = False
    sneak_attack_d6: int = Field(default=0, ge=0, le=10)
    cunning_action: bool = False
    stationary_bonus_action_next_attack_advantage: bool = False
    cunning_strike_trip_die_cost: int = Field(default=0, ge=0, le=6)
    cunning_strike_obscure_die_cost: int = Field(default=0, ge=0, le=6)
    cunning_strike_max_effects: int = Field(default=0, ge=0, le=2)
    uncanny_dodge: bool = False
    evasion: bool = False
    martial_arts_bonus_attack: bool = False
    martial_arts_die_size: int = Field(default=0, ge=0, le=12)
    flurry_of_blows: bool = False
    deflect_missiles: bool = False
    open_hand_technique: bool = False
    stunning_strike: bool = False
    divine_smite_2014: bool = False
    turn_unholy_2014: bool = False
    aura_of_protection_2014_bonus: int = Field(default=0, ge=0, le=10)
    aura_radius_2014_ft: int = Field(default=0, ge=0, le=30)
    aura_of_devotion_2014: bool = False
    aura_of_courage_2014: bool = False
    sacred_weapon_2014_bonus: int = Field(default=0, ge=0, le=10)
    survivor_heal_amount: int = Field(default=0, ge=0, le=30)
    bloodied_start_turn_heal_amount: int = Field(default=0, ge=0, le=40)
    death_save_advantage: bool = False
    death_save_recovery_minimum: int = Field(default=20, ge=2, le=20)
    critical_move_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    tactical_shift_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
