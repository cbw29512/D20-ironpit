from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import ConditionName
from app.domain.runtime import TimedTurnBehavior


class TurningEffectDefinition(BaseModel):
    """Declarative lifecycle for one failed turning save."""

    condition_ids: list[ConditionName] = Field(default_factory=list)
    duration_rounds: int = Field(default=10, ge=1, le=100)
    turn_behavior: TimedTurnBehavior = "forced_retreat"
    ends_on_damage: bool = True
    ends_if_source_unconscious: bool = False
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False
    suppresses_reactions: bool = False
