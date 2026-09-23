from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.grid import GridPosition
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


class PersistentSpellAttackAction(BaseModel):
    """Immutable source data for a mobile spell effect that repeats spell attacks."""

    id: str
    name: str
    attack: SpellAttackAction
    duration_rounds: int = Field(ge=1, le=600)
    move_ft: int = Field(ge=0)
    attack_reach_ft: int = Field(default=5, ge=0)
    upcast_interval_levels: int = Field(default=1, ge=1, le=9)

    @model_validator(mode="after")
    def validate_action(self) -> "PersistentSpellAttackAction":
        try:
            if self.attack.id != self.id or self.attack.name != self.name:
                raise ValueError("Persistent spell attack identity must match its attack definition.")
            if self.attack.level <= 0:
                raise ValueError("Persistent spell attack requires a leveled spell.")
            if self.attack.action_cost != "bonus_action":
                raise ValueError("Persistent spell attack casting must use a Bonus Action.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Persistent spell attack schema validation failed for %s.", self.id)
            raise RuntimeError("Persistent spell attack schema could not be validated.") from exc


class PersistentSpellAttackState(BaseModel):
    """Fresh per-fight position, slot level, and expiry for one active spell effect."""

    action_id: str
    slot_level: int = Field(ge=1, le=9)
    position: GridPosition
    applied_round: int = Field(ge=1)
    expires_round: int = Field(ge=2)
