from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


class PersistentSuppressionZoneAction(BaseModel):
    """Stationary zone that suppresses sound, verbal casting, and thunder."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    cast_range_ft: int = Field(ge=0)
    radius_ft: int = Field(ge=5)
    duration_rounds: int = Field(ge=1)
    concentration: bool = False
    deafens: bool = True
    blocks_verbal_spells: bool = True
    thunder_immunity: bool = True
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    expends_spell_slot: bool = False
    animation: str = "silence"
    source: str | None = None

    @model_validator(mode="after")
    def validate_zone(self) -> "PersistentSuppressionZoneAction":
        try:
            slot_resource = bool(self.resource_id and self.resource_id.startswith("spell-slot-"))
            if slot_resource != self.expends_spell_slot:
                raise ValueError("Suppression-zone spell-slot resource and expends_spell_slot must agree.")
            if self.radius_ft % 5:
                raise ValueError("Suppression zones must use 5-foot increments.")
            if not (self.deafens or self.blocks_verbal_spells or self.thunder_immunity):
                raise ValueError("Suppression zones require at least one suppression effect.")
            return self
        except Exception:
            logger.exception("Suppression zone schema validation failed for %s.", self.id)
            raise


class PersistentSuppressionZoneState(BaseModel):
    """Mutable per-fight placement for one suppression zone."""

    zone_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    position: GridPosition
    radius_ft: int = Field(ge=5)
    expires_round: int = Field(ge=1)
    deafens: bool = True
    blocks_verbal_spells: bool = True
    thunder_immunity: bool = True
    concentration: bool = False
