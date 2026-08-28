from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.combatants import BattlefieldState, CombatantState, DamageType


class RollMode(StrEnum):
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


class DiceRoll(BaseModel):
    notation: str
    rolls: list[int]
    modifier: int = 0
    selected_roll: int | None = None
    mode: RollMode = RollMode.NORMAL
    total: int


class DamageRollComponent(BaseModel):
    source: str
    notation: str
    rolls: list[int]
    modifier: int = 0
    damage_type: DamageType
    total: int


class CombatCardEffectChange(BaseModel):
    actor_id: str
    effect_id: str
    operation: Literal["apply", "remove"]
    kind: Literal["buff", "debuff"] | None = None
    label: str | None = None
    detail: str | None = None


class BattleEvent(BaseModel):
    sequence: int
    round_number: int
    event_type: Literal[
        "initiative", "movement", "dash", "disengage", "dodge", "hide", "search",
        "status", "attack", "healing", "victory", "draw"
    ]
    actor_id: str
    actor_name: str
    target_id: str | None = None
    target_name: str | None = None
    attack_roll: DiceRoll | None = None
    check_roll: DiceRoll | None = None
    damage_roll: DiceRoll | None = None
    damage_components: list[DamageRollComponent] = Field(default_factory=list)
    effect_changes: list[CombatCardEffectChange] = Field(default_factory=list)
    healing_roll: DiceRoll | None = None
    hit: bool | None = None
    critical: bool = False
    hp_before: int | None = None
    hp_after: int | None = None
    distance_before_ft: int | None = None
    distance_after_ft: int | None = None
    movement_ft: int | None = None
    weapon_id: str | None = None
    projectile: str | None = None
    feature_id: str | None = None
    reaction_id: str | None = None
    resource_remaining: int | None = None
    log_visible: bool = True
    animation: str
    description: str


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
