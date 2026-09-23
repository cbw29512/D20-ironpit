from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, ConditionName, ConditionTiming
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class TimedSelfBuffAction(BaseModel):
    """Declarative self-buff composed from universal condition and resistance mechanics."""

    id: str
    name: str
    action_cost: ActionCost = "action"
    resource_id: str
    resource_cost: int = Field(default=1, ge=1, le=200)
    duration_rounds: int = Field(ge=1, le=600)
    condition_ids: list[ConditionName] = Field(min_length=1)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    expiry_timing: ConditionTiming = "source_turn_start"
    priority: int = 0
    animation: str = "buff"

    @model_validator(mode="after")
    def validate_on_turn_activation(self) -> "TimedSelfBuffAction":
        try:
            if self.action_cost == "reaction":
                raise ValueError("Timed self-buff Actions currently require an on-turn Action or Bonus Action.")
            if len(set(self.condition_ids)) != len(self.condition_ids):
                raise ValueError("Timed self-buff condition ids must be unique.")
            if len(set(self.damage_resistances)) != len(self.damage_resistances):
                raise ValueError("Timed self-buff damage resistances must be unique.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Timed self-buff schema validation failed for %s.", self.id)
            raise RuntimeError("Timed self-buff schema could not be validated.") from exc
