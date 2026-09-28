from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class AlternateSpellCastGrant(BaseModel):
    """Permission to cast one declared spell at a fixed level without expending a spell slot."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    spell_id: str = Field(min_length=1)
    cast_level: int = Field(ge=1, le=9)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    priority: int = 0

    @model_validator(mode="after")
    def validate_resource(self) -> "AlternateSpellCastGrant":
        try:
            if self.resource_id is None and self.resource_cost != 1:
                raise ValueError("Unlimited alternate spell casts must use the default resource cost.")
            return self
        except Exception:
            logger.exception("Failed to validate alternate spell cast grant %s.", self.source_id)
            raise
