from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class FreeSpellCastGrant(BaseModel):
    """Source-neutral permission to cast one spell without expending a spell slot."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    spell_id: str = Field(min_length=1)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_resource(self) -> "FreeSpellCastGrant":
        try:
            if self.resource_id is None and self.resource_cost != 1:
                raise ValueError("At-will free spell casts cannot define a resource cost.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Failed to validate free spell-cast grant %s.", self.source_id)
            raise RuntimeError("Free spell-cast grant could not be validated.") from exc
