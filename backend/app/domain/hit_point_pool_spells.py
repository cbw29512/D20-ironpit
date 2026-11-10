"""Source-neutral spell that allocates one rolled HP pool and applies a timed condition."""
from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from app.domain.actions import ActionCost, ConditionTiming

logger = logging.getLogger(__name__)


class HitPointPoolSpellAction(BaseModel):
    """Immutable spell definition; resources and timed effects belong to fight state."""

    id: str
    name: str
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    area_radius_ft: int = Field(ge=5)
    pool_dice_count: int = Field(ge=1, le=60)
    pool_dice_size: int = Field(ge=2, le=100)
    extra_dice_per_upcast_level: int = Field(default=0, ge=0, le=20)
    target_order: Literal["ascending_current_hp"] = "ascending_current_hp"
    condition_id: str
    duration_rounds: int = Field(ge=1, le=100800)
    expiry_timing: ConditionTiming = "source_turn_start"
    skip_unconscious: bool = True
    ends_on_damage: bool = True
    excluded_creature_types: list[str] = Field(default_factory=list)
    excluded_condition_immunities: list[str] = Field(default_factory=list)
    allowed_removal_action_ids: list[str] = Field(default_factory=list)
    animation: str = "spell-control"
    source: str | None = None

    @model_validator(mode="after")
    def validate_pool(self) -> "HitPointPoolSpellAction":
        try:
            if not self.id or not self.name or not self.condition_id:
                raise ValueError("HP-pool spells require id, name, and condition.")
            if self.pool_dice_count + (9 - self.level) * self.extra_dice_per_upcast_level > 100:
                raise ValueError("HP-pool spell has an unsupported maximum dice count.")
            if len(set(self.excluded_creature_types)) != len(self.excluded_creature_types):
                raise ValueError("HP-pool creature exclusions must be unique.")
            if len(set(self.excluded_condition_immunities)) != len(self.excluded_condition_immunities):
                raise ValueError("HP-pool condition exclusions must be unique.")
            return self
        except Exception:
            logger.exception("Invalid HP-pool spell action %s.", self.id)
            raise
