from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.combatants import DamageType


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
        "roll", "revision", "check", "damage", "defense", "hp", "temp_hp",
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
