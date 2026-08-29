from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import GrappleSource
from app.domain.combatants import CombatantTemplate, DamageType


class ResourceState(BaseModel):
    id: str
    name: str
    current_uses: int = Field(ge=0)
    max_uses: int = Field(ge=0)


class TimedEffect(BaseModel):
    effect_id: str
    source_id: str
    expires_at_start_of_source_turn: bool = True


class DemoRoster(BaseModel):
    fighter: CombatantTemplate
    monster: CombatantTemplate


class ArenaRoster(BaseModel):
    characters: list[CombatantTemplate]
    monsters: list[CombatantTemplate]


class CombatantState(BaseModel):
    template: CombatantTemplate
    current_hp: int
    temporary_hp: int = Field(default=0, ge=0)
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
    movement_remaining_ft: int = Field(default=0, ge=0)
    resources: list[ResourceState] = Field(default_factory=list)
    active_effect_ids: list[str] = Field(default_factory=list)
    grapple_sources: list[GrappleSource] = Field(default_factory=list)
    timed_effects: list[TimedEffect] = Field(default_factory=list)
    feature_last_turn_keys: dict[str, str] = Field(default_factory=dict)
    temporary_damage_resistances: list[DamageType] = Field(default_factory=list)
    rage_expires_round: int | None = Field(default=None, ge=1)
    rage_max_round: int | None = Field(default=None, ge=1)


class BattlefieldState(BaseModel):
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)
