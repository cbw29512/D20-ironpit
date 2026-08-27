from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.domain.combatants import CombatantTemplate


class RulesCoverage(StrEnum):
    FULLY_IMPLEMENTED = "fully_implemented"
    ARENA_ASSUMPTION = "arena_assumption"
    UNSUPPORTED = "unsupported"


class RulesCoverageItem(BaseModel):
    feature_id: str = Field(min_length=1)
    coverage: RulesCoverage
    note: str | None = None


class CatalogEntry(BaseModel):
    combatant: CombatantTemplate
    tags: list[str] = Field(default_factory=list)
    battle_ready: bool = True
    rules_coverage: list[RulesCoverageItem] = Field(default_factory=list)


class BattleRequest(BaseModel):
    character_id: str = Field(min_length=1)
    monster_id: str = Field(min_length=1)
    starting_distance_ft: int = Field(default=5, ge=0, le=1000)
