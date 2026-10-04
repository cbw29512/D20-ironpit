from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost

logger = logging.getLogger(__name__)


class TeleportAction(BaseModel):
    """Voluntary teleport that uses the shared teleport movement source."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=5)
    passenger_count: int = Field(default=0, ge=0, le=4)
    passenger_range_ft: int = Field(default=5, ge=0)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    expends_spell_slot: bool = False
    animation: str = "teleport"
    source: str | None = None

    @model_validator(mode="after")
    def validate_teleport(self) -> "TeleportAction":
        try:
            slot_resource = bool(self.resource_id and self.resource_id.startswith("spell-slot-"))
            if slot_resource != self.expends_spell_slot:
                raise ValueError("Teleport spell-slot resource and expends_spell_slot must agree.")
            if self.passenger_count and self.passenger_range_ft <= 0:
                raise ValueError("Passenger teleports require a positive passenger range.")
            return self
        except Exception:
            logger.exception("Teleport action schema validation failed for %s.", self.id)
            raise
