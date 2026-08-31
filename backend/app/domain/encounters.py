from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.events import BattleEvent
from app.domain.runtime import CombatantState


EncounterSide = Literal["heroes", "monsters"]
EncounterOutcome = Literal["active", "heroes_win", "monsters_win", "draw"]


class EncounterSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hero_ids: list[str] = Field(min_length=1, max_length=6)
    monster_ids: list[str] = Field(min_length=1, max_length=6)


class EncounterCombatant(BaseModel):
    combatant_id: str
    side: EncounterSide
    position_ft: int = Field(ge=0)
    state: CombatantState


class EncounterSetup(BaseModel):
    heroes: list[EncounterCombatant] = Field(min_length=1, max_length=6)
    monsters: list[EncounterCombatant] = Field(min_length=1, max_length=6)
    hero_total_levels: int = Field(ge=1, le=120)
    monster_total_cr: str


class InitiativeGroup(BaseModel):
    side: EncounterSide
    template_id: str
    combatant_ids: list[str] = Field(min_length=1, max_length=6)
    natural_roll: int = Field(ge=1, le=20)
    initiative_bonus: int
    initiative_count: int
    tie_break_roll: int | None = Field(default=None, ge=1, le=20)


class EncounterInitiative(BaseModel):
    groups: list[InitiativeGroup] = Field(min_length=2, max_length=12)
    turn_order: list[str] = Field(min_length=2, max_length=12)


class EncounterBattleResult(BaseModel):
    battle_id: str
    outcome: EncounterOutcome
    rounds: int = Field(ge=0)
    setup: EncounterSetup
    initiative: EncounterInitiative
    events: list[BattleEvent] = Field(default_factory=list)
    ruleset: str = "SRD 5.2.1 combat subset"
