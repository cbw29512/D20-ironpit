from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


class PersistentSuppressionZoneAction(BaseModel):
    """Persistent zone that suppresses sound, sight, verbal casting, or damage."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    cast_range_ft: int = Field(ge=0)
    radius_ft: int = Field(ge=5)
    duration_rounds: int = Field(ge=1)
    center_on_source: bool = False
    follows_source: bool = False
    is_spell: bool = True
    concentration: bool = False
    deafens: bool = True
    blocks_verbal_spells: bool = True
    thunder_immunity: bool = True
    # Generic visibility suppression; magical darkness is not Blinded.
    obscuration_kind: Literal["none", "magical-darkness", "heavy-physical"] = "none"
    # Retain printed Darkness-style light-dispel ceilings. The current arena
    # exposes no spell-created light zone, so there is no legal target yet.
    dispel_light_spell_max_level: int | None = Field(default=None, ge=0, le=9)
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
            if self.follows_source and not self.center_on_source:
                raise ValueError("A source-following suppression zone must be source-centered.")
            if self.center_on_source and self.cast_range_ft != 0:
                raise ValueError("A source-centered suppression zone must have zero cast range.")
            if not (self.deafens or self.blocks_verbal_spells or self.thunder_immunity
                or self.obscuration_kind != "none"):
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
    follows_source: bool = False
    deafens: bool = True
    blocks_verbal_spells: bool = True
    thunder_immunity: bool = True
    obscuration_kind: Literal["none", "magical-darkness", "heavy-physical"] = "none"
    dispel_light_spell_max_level: int | None = Field(default=None, ge=0, le=9)
    concentration: bool = False
