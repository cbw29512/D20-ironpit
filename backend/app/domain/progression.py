from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal

from app.domain.character_builds import AbilityName


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


class ProgressionCombatFeatures(BaseModel):
    """Level/subclass combat flags that should stay out of core stat-block shape."""

    effect_bound_survival_save: EffectBoundSurvivalSave | None = None
    turning_failure_damage: AbilityScaledDamageRider | None = None
    slot_healing_other_self_rider: SlotHealingSelfRider | None = None
    ability_check_minimums: list[AbilityCheckMinimum] = Field(default_factory=list)
    critical_hit_minimum: int = Field(default=20, ge=2, le=20)
    initiative_advantage: bool = False
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
    aura_of_devotion_2014: bool = False
    aura_of_courage_2014: bool = False
    sacred_weapon_2014_bonus: int = Field(default=0, ge=0, le=10)
    survivor_heal_amount: int = Field(default=0, ge=0, le=30)
    critical_move_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    tactical_shift_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
