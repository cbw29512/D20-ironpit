from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, GrappleSource
from app.domain.attachments import AttachmentState
from app.domain.combatants import CombatantTemplate, DamageType
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.modifiers import CombatModifier, ConcentrationState
from app.domain.ongoing_hp_loss import OngoingHpLossState
from app.domain.resource_state import ResourceState
from app.domain.timed_effects import TimedEffect, TimedTurnBehavior
from app.domain.swallow import SwallowedState

class DemoRoster(BaseModel):
    fighter: CombatantTemplate
    monster: CombatantTemplate


class ArenaRoster(BaseModel):
    characters: list[CombatantTemplate]
    monsters: list[CombatantTemplate]


class CombatantState(BaseModel):
    template: CombatantTemplate
    current_hp: int
    max_hp_bonus: int = Field(default=0, ge=0)
    max_hp_reduction: int = Field(default=0, ge=0)
    temporary_hp: int = Field(default=0, ge=0)
    ability_score_reductions: dict[AbilityName, int] = Field(default_factory=dict)
    damage_types_since_last_turn: list[DamageType] = Field(default_factory=list)
    position: GridPosition | None = None
    initiative_roll: int | None = None
    initiative_total: int | None = None
    is_alive: bool = True
    is_unconscious: bool = False
    is_stable: bool = False
    is_dead: bool = False
    death_save_successes: int = Field(default=0, ge=0, le=3)
    death_save_failures: int = Field(default=0, ge=0, le=3)
    action_available: bool = True
    bonus_action_available: bool = True
    reaction_available: bool = True
    turn_terminated: bool = False
    turn_termination_reason: str | None = None
    heroic_inspiration: bool = False
    movement_remaining_ft: int = Field(default=0, ge=0)
    resources: list[ResourceState] = Field(default_factory=list)
    legendary_action_uses_remaining: int = Field(default=0, ge=0)
    legendary_action_locked_option_ids: list[str] = Field(default_factory=list)
    active_effect_ids: list[str] = Field(default_factory=list)
    active_buff_effect_ids: list[str] = Field(default_factory=list)
    source_effect_immunities: list[str] = Field(default_factory=list)
    opening_buff_spell_id: str | None = None
    grapple_sources: list[GrappleSource] = Field(default_factory=list)
    swallowed: SwallowedState | None = None
    attachment: AttachmentState | None = None
    timed_effects: list[TimedEffect] = Field(default_factory=list)
    ongoing_hp_loss_effects: list[OngoingHpLossState] = Field(default_factory=list)
    active_modifiers: list[CombatModifier] = Field(default_factory=list)
    concentration: ConcentrationState | None = None
    feature_last_turn_keys: dict[str, str] = Field(default_factory=dict)
    spell_slot_expended_turn_key: str | None = None
    temporary_damage_resistances: list[DamageType] = Field(default_factory=list)
    rage_expires_round: int | None = Field(default=None, ge=1)
    rage_max_round: int | None = Field(default=None, ge=1)


class BattlefieldState(BaseModel):
    map_definition: BattleMapDefinition | None = None
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)
