from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)

EnvironmentContextId = Literal["sunlight"]
EnvironmentContextRollKind = Literal["attack_rolls", "sight_based_perception_checks"]


class EmittedEnvironmentContext(BaseModel):
    """Source-owned battlefield/environment fact emitted by an active effect."""

    context_id: EnvironmentContextId
    radius_ft: int = Field(ge=1, le=120)

    @model_validator(mode="after")
    def validate_emission(self) -> "EmittedEnvironmentContext":
        try:
            if self.radius_ft < 1:
                raise ValueError("Emitted environment context requires a positive radius.")
            return self
        except Exception:
            logger.exception("Emitted environment context schema validation failed.")
            raise


class EnvironmentContextReaction(BaseModel):
    """Target-owned declarative reaction to a live battlefield/environment context."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    context_id: EnvironmentContextId
    disadvantage_on: list[EnvironmentContextRollKind] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_reaction(self) -> "EnvironmentContextReaction":
        try:
            if any(not item.strip() for item in (self.source_id, self.source_name)):
                raise ValueError("Environment context reactions require a source id and name.")
            if len(set(self.disadvantage_on)) != len(self.disadvantage_on):
                raise ValueError("Environment context reaction roll kinds must be unique.")
            return self
        except Exception:
            logger.exception(
                "Invalid environment context reaction %s for %s.",
                self.source_id,
                self.context_id,
            )
            raise
