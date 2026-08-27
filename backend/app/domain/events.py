from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.abilities import Ability, Skill
from app.domain.combatants import BattlefieldState, CombatantState, DamageType
from app.domain.conditions import ConditionType


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


class BattleEvent(BaseModel):
    sequence: int
    round_number: int
    event_type: Literal[
        "initiative",
        "movement",
        "forced_movement",
        "condition",
        "saving_throw",
        "ability_check",
        "dash",
        "attack",
        "healing",
        "feature",
        "victory",
        "draw",
    ]
    actor_id: str
    actor_name: str
    target_id: str | None = None
    target_name: str | None = None
    attack_roll: DiceRoll | None = None
    saving_throw: DiceRoll | None = None
    ability_check: DiceRoll | None = None
    test_dc: int | None = None
    test_ability: Ability | None = None
    test_skill: Skill | None = None
    test_success: bool | None = None
    damage_roll: DiceRoll | None = None
    damage_components: list[DamageRollComponent] = Field(default_factory=list)
    damage_applied: int | None = None
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
    condition: ConditionType | None = None
    condition_active: bool | None = None
    resource_remaining: int | None = None
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
