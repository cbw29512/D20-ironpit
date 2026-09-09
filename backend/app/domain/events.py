from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.event_support import (
    AuditPhase,
    AuditStep,
    DamageRollComponent,
    DiceRoll,
    EventAudit,
    RollMode,
    RollRevision,
)
from app.domain.grid import GridPosition
from app.domain.runtime import BattlefieldState, CombatantState


class BattleEvent(BaseModel):
    sequence: int
    round_number: int
    event_type: Literal[
        "initiative", "movement", "dash", "attack", "saving_throw", "healing",
        "feature", "death_save", "victory", "draw",
    ]
    actor_id: str
    actor_name: str
    target_id: str | None = None
    target_name: str | None = None
    attack_name: str | None = None
    target_ac: int | None = Field(default=None, ge=0)
    attack_roll: DiceRoll | None = None
    saving_throw_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = Field(default=None, ge=1)
    save_succeeded: bool | None = None
    ability_check_roll: DiceRoll | None = None
    check_ability: str | None = None
    check_dc: int | None = Field(default=None, ge=1)
    check_succeeded: bool | None = None
    damage_roll: DiceRoll | None = None
    death_save_roll: DiceRoll | None = None
    damage_components: list[DamageRollComponent] = Field(default_factory=list)
    applied_condition_ids: list[str] = Field(default_factory=list)
    removed_condition_ids: list[str] = Field(default_factory=list)
    healing_roll: DiceRoll | None = None
    hit: bool | None = None
    critical: bool = False
    turn_terminated: bool = False
    turn_termination_reason: str | None = None
    hp_before: int | None = None
    hp_after: int | None = None
    temporary_hp_before: int | None = Field(default=None, ge=0)
    temporary_hp_after: int | None = Field(default=None, ge=0)
    death_save_successes_before: int | None = Field(default=None, ge=0, le=3)
    death_save_failures_before: int | None = Field(default=None, ge=0, le=3)
    death_save_successes: int | None = Field(default=None, ge=0, le=3)
    death_save_failures: int | None = Field(default=None, ge=0, le=3)
    is_stable: bool | None = None
    is_dead: bool | None = None
    distance_before_ft: int | None = None
    distance_after_ft: int | None = None
    movement_ft: int | None = None
    grid_position_before: GridPosition | None = None
    grid_position_after: GridPosition | None = None
    grid_path: list[GridPosition] = Field(default_factory=list)
    weapon_id: str | None = None
    projectile: str | None = None
    feature_id: str | None = None
    concentration_started_effect_id: str | None = None
    concentration_ended_effect_id: str | None = None
    resource_remaining: int | None = None
    animation: str
    description: str
    audit: EventAudit | None = None


class BattleResult(BaseModel):
    battle_id: str
    winner_id: str | None
    winner_name: str | None
    rounds: int
    fighter: CombatantState
    monster: CombatantState
    battlefield: BattlefieldState
    events: list[BattleEvent]
    ruleset: str = "SRD 5.2.1 subset"
