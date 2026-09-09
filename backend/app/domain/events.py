from __future__ import annotations
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.combatants import DamageType
from app.domain.runtime import BattlefieldState, CombatantState


class RollMode(StrEnum):
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


class AuditPhase(StrEnum):
    PRECOMBAT = "precombat"
    INITIATIVE = "initiative"
    ACTION_SELECTION = "action_selection"
    BEFORE_ROLL = "before_roll"
    ROLL = "roll"
    REROLL_OR_REPLACEMENT = "reroll_or_replacement"
    HIT_OR_SAVE_CHECK = "hit_or_save_check"
    DAMAGE_ROLL = "damage_roll"
    DAMAGE_APPLIED = "damage_applied"
    STATE_CHANGE = "state_change"
    RESOURCE_CHANGE = "resource_change"
    TURN_END = "turn_end"
    COMBAT_END = "combat_end"


class RollRevision(BaseModel):
    source_effect_id: str
    kind: Literal["die_replacement", "full_reroll", "roll_twice_choose"]
    original_rolls: list[int]
    replacement_rolls: list[int]
    original_modifier: int = 0
    replacement_modifier: int = 0
    original_selected: int | None = None
    replacement_selected: int | None = None
    original_total: int
    replacement_total: int
    accepted: Literal["original", "replacement"]
    replaced_die_index: int | None = Field(default=None, ge=0)


class AuditStep(BaseModel):
    phase: AuditPhase
    kind: Literal[
        "roll", "revision", "check", "damage", "defense", "hp", "max_hp", "temp_hp",
        "condition", "concentration", "resource", "outcome", "rule",
    ]
    label: str


class EventAudit(BaseModel):
    schema_version: int = Field(default=1, ge=1)
    steps: list[AuditStep] = Field(default_factory=list)


class DiceRoll(BaseModel):
    notation: str
    rolls: list[int]
    modifier: int = 0
    selected_roll: int | None = None
    mode: RollMode = RollMode.NORMAL
    total: int
    revisions: list[RollRevision] = Field(default_factory=list)


class DamageRollComponent(BaseModel):
    source: str
    notation: str
    rolls: list[int]
    modifier: int = 0
    damage_type: DamageType
    total: int
    applied_total: int | None = Field(default=None, ge=0)
    revisions: list[RollRevision] = Field(default_factory=list)


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
    max_hp_before: int | None = Field(default=None, ge=0)
    max_hp_after: int | None = Field(default=None, ge=0)
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
