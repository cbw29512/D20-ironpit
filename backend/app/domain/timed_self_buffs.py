from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, ConditionName

logger = logging.getLogger(__name__)


class TimedSelfBuffAction(BaseModel):
    """Declarative self-buff composed from shared condition and concentration primitives."""

    id: str
    name: str
    action_cost: ActionCost = "action"
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    duration_rounds: int | None = Field(default=None, ge=1, le=600)
    condition_ids: list[ConditionName] = Field(default_factory=list)
    magical_effect: bool = False
    concentration: bool = False
    ends_on_owner_attack: bool = False
    ends_on_owner_spell_cast: bool = False
    priority: int = 0
    animation: str = "buff"

    @model_validator(mode="after")
    def validate_buff(self) -> "TimedSelfBuffAction":
        try:
            if self.action_cost == "reaction":
                raise ValueError("Timed self buffs require an Action or Bonus Action.")
            if len(set(self.condition_ids)) != len(self.condition_ids):
                raise ValueError("Timed self-buff conditions must be unique.")
            if not self.condition_ids and not self.concentration:
                raise ValueError("Timed self buff requires at least one state effect.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Timed self-buff validation failed for %s.", self.id)
            raise RuntimeError("Timed self-buff schema could not be validated.") from exc
