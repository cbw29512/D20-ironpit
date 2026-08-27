from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class DamageType(StrEnum):
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"


class Weapon(BaseModel):
    name: str
    attack_bonus: int
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int
    damage_type: DamageType
    animation: str


class VisualLoadout(BaseModel):
    armor: str
    main_hand: str
    off_hand: str | None = None
    body_style: str = "humanoid"


class CombatantTemplate(BaseModel):
    id: str
    name: str
    level: int | None = Field(default=None, ge=1, le=20)
    kind: Literal["character", "monster"]
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    initiative_bonus: int
    weapon: Weapon
    visual: VisualLoadout
    source: str


class CombatantState(BaseModel):
    template: CombatantTemplate
    current_hp: int
    initiative_roll: int | None = None
    initiative_total: int | None = None
    is_alive: bool = True


class DiceRoll(BaseModel):
    notation: str
    rolls: list[int]
    modifier: int = 0
    total: int


class BattleEvent(BaseModel):
    sequence: int
    round_number: int
    event_type: Literal["initiative", "attack", "victory", "draw"]
    actor_id: str
    actor_name: str
    target_id: str | None = None
    target_name: str | None = None
    attack_roll: DiceRoll | None = None
    damage_roll: DiceRoll | None = None
    hit: bool | None = None
    critical: bool = False
    hp_before: int | None = None
    hp_after: int | None = None
    animation: str
    description: str


class BattleResult(BaseModel):
    battle_id: str
    winner_id: str | None
    winner_name: str | None
    rounds: int
    fighter: CombatantState
    monster: CombatantState
    events: list[BattleEvent]
    ruleset: str = "SRD 5.2.1 subset"
