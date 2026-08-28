from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DuelMode(StrEnum):
    OPEN = "open"
    MELEE = "melee"
    RANGED = "ranged"
    CLOSE = "close"


class PrecombatActorPlan(BaseModel):
    attempt_hide: bool = False
    ambush_target_ids: set[str] = Field(default_factory=set)


class EncounterSetup(BaseModel):
    plans_by_actor: dict[str, PrecombatActorPlan] = Field(default_factory=dict)
