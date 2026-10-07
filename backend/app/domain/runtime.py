from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import GrappleSource
from app.domain.combatants import CombatantTemplate, DamageType
from app.domain.damage_sources import ConditionalDamageDefense
from app.domain.d20_bonus_dice import ActiveD20BonusDieGrant
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.modifiers import CombatModifier, ConcentrationState
from app.domain.persistent_spell_attacks import PersistentSpellAttackState
from app.domain.replacement_forms import ReplacementFormState
from app.domain.timed_effects import TimedEffect, TimedTurnBehavior


class ResourceState(BaseModel):
    id: str
    name: str
    current_uses: int = Field(ge=0)
    max_uses: int = Field(ge=0)


class DeferredEffectState(BaseModel):
    """Fresh per-fight state for one armed deferred source/target relationship."""

    source_id: str
    target_id: str
    armed_round: int = Field(ge=1)


class DelayedResourceRefillState(BaseModel):
    source_id: str
    started_round: int = Field(ge=1)
    completes_round: int = Field(ge=1)


class DemoRoster(BaseModel):
    fighter: CombatantTemplate
    monster: CombatantTemplate


class ArenaRoster(BaseModel):
    characters: list[CombatantTemplate]
    monsters: list[CombatantTemplate]


class CombatantState(BaseModel):
    template: CombatantTemplate
    current_hp: int
    current_round: int | None = Field(default=None, ge=1)
    turns_started: int = Field(default=0, ge=0)
    max_hp_bonus: int = Field(default=0, ge=0)
    temporary_hp: int = Field(default=0, ge=0)
    position: GridPosition | None = None
    formation_row: Literal["front", "back"] | None = None
    initial_formation_row: Literal["front", "back"] | None = None
    initiative_roll: int | None = None
    initiative_total: int | None = None
    is_alive: bool = True
    is_unconscious: bool = False
    is_stable: bool = False
    is_dead: bool = False
    exhaustion_level: int = Field(default=0, ge=0, le=6)
    death_save_successes: int = Field(default=0, ge=0, le=3)
    death_save_failures: int = Field(default=0, ge=0, le=3)
    action_available: bool = True
    bonus_action_available: bool = True
    reaction_available: bool = True
    disengaged_this_turn: bool = False
    turn_terminated: bool = False
    turn_termination_reason: str | None = None
    heroic_inspiration: bool = False
    dash_uses_this_turn: int = Field(default=0, ge=0)
    attacks_this_turn: int = Field(default=0, ge=0)
    movement_remaining_ft: int = Field(default=0, ge=0)
    voluntary_turn_activity: Literal["movement", "action", "bonus_action"] | None = None
    resources: list[ResourceState] = Field(default_factory=list)
    active_effect_ids: list[str] = Field(default_factory=list)
    active_buff_effect_ids: list[str] = Field(default_factory=list)
    opening_buff_id: str | None = None
    grapple_sources: list[GrappleSource] = Field(default_factory=list)
    timed_effects: list[TimedEffect] = Field(default_factory=list)
    deferred_effects: list[DeferredEffectState] = Field(default_factory=list)
    delayed_resource_refills: list[DelayedResourceRefillState] = Field(default_factory=list)
    persistent_spell_attacks: list[PersistentSpellAttackState] = Field(default_factory=list)
    active_modifiers: list[CombatModifier] = Field(default_factory=list)
    targeting_gate_immunity_keys: list[str] = Field(default_factory=list)
    active_d20_bonus_dice: list[ActiveD20BonusDieGrant] = Field(default_factory=list)
    concentration: ConcentrationState | None = None
    replacement_form: ReplacementFormState | None = None
    survival_save_uses: dict[str, int] = Field(default_factory=dict)
    pending_survival_save_logs: list[str] = Field(default_factory=list)
    pending_zero_hp_replacement_logs: list[str] = Field(default_factory=list)
    feature_last_turn_keys: dict[str, str] = Field(default_factory=dict)
    feature_use_counts: dict[str, int] = Field(default_factory=dict)
    spell_slot_expended_turn_key: str | None = None
    temporary_damage_resistances: list[DamageType] = Field(default_factory=list)
    zone_damage_immunities: list[DamageType] = Field(default_factory=list)
    active_conditional_damage_defenses: list[ConditionalDamageDefense] = Field(default_factory=list)
    hit_point_maximum_reduction: int = Field(default=0, ge=0)
    ability_score_reductions: dict[str, int] = Field(default_factory=dict)
    active_curses: list[str] = Field(default_factory=list)
    damage_share_source_id: str | None = None
    damage_share_range_ft: int = Field(default=0, ge=0)
    damage_share_effect_id: str | None = None
    emanation_triggers_this_turn: dict[str, str] = Field(default_factory=dict)
    rage_expires_round: int | None = Field(default=None, ge=1)
    rage_max_round: int | None = Field(default=None, ge=1)
    damage_types_taken_since_regen: list[str] = Field(default_factory=list)
    damage_taken_this_turn_by_type: dict[str, int] = Field(default_factory=dict)
    triggered_extra_attack_stack_counts: dict[str, int] = Field(default_factory=dict)
    source_owned_exhaustion_levels: dict[str, int] = Field(default_factory=dict)


class BattlefieldState(BaseModel):
    map_definition: BattleMapDefinition | None = None
    # Migration-only scalar distance fields. Remove after all canonical paths consume grid positions.
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)
