from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.combatants import CombatantState


class EncounterSelection(BaseModel):
    hero_ids: list[str] = Field(min_length=1)
    monster_ids: list[str] = Field(min_length=1)
    starting_distance_ft: int = Field(default=30, ge=0)


class EncounterCombatant(BaseModel):
    combatant_id: str
    side: Literal["heroes", "monsters"]
    position_ft: int = Field(ge=0)
    state: CombatantState


class EncounterSetup(BaseModel):
    heroes: list[EncounterCombatant] = Field(min_length=1)
    monsters: list[EncounterCombatant] = Field(min_length=1)
    starting_distance_ft: int = Field(ge=0)
