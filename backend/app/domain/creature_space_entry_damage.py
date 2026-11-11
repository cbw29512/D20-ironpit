"""Source-defined damage and recurring effect on entering a another creature's occupied square."""
from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.recurring_damage import OnHitRecurringDamage
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class CreatureSpaceEntryDamage(BaseModel):
    """An immutable entry trigger; the mover's turn ledger enforces once per target."""

    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    recurring_damage: OnHitRecurringDamage

    @model_validator(mode="after")
    def validate_recurring_damage(self) -> "CreatureSpaceEntryDamage":
        try:
            if self.recurring_damage.tick_timing != "target_turn_start":
                raise ValueError("Entry ignition requires a target-turn-start recurrence.")
            if self.recurring_damage.damage_type != self.damage_type:
                raise ValueError("Entry and recurring damage must have matching types.")
            return self
        except Exception:
            logger.exception("Invalid creature-space-entry damage specification.")
            raise
