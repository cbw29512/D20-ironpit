from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

EnvironmentContextId = Literal["sunlight", "bright_light"]
EnvironmentContextActionCost = Literal["action", "bonus_action"]
EnvironmentContextRollKind = Literal[
    "attack_rolls", "ability_checks", "saving_throws",
    "sight_based_perception_checks",
]


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


class EnvironmentContextMode(BaseModel):
    """One source-declared fight-local environment mode."""

    id: str = Field(min_length=1)
    emitted_contexts: list[EmittedEnvironmentContext] = Field(default_factory=list)


class EnvironmentContextControlAction(BaseModel):
    """An Action or Bonus Action that changes a source-owned context mode."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    action_cost: EnvironmentContextActionCost
    initial_mode_id: str = Field(min_length=1)
    ai_mode_id: str = Field(min_length=1)
    modes: list[EnvironmentContextMode] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_modes(self) -> "EnvironmentContextControlAction":
        ids = [mode.id for mode in self.modes]
        if len(ids) != len(set(ids)):
            raise ValueError("Environment context modes must have unique ids.")
        if self.initial_mode_id not in ids or self.ai_mode_id not in ids:
            raise ValueError("Initial and AI environment modes must reference declared modes.")
        return self


class EnvironmentContextReaction(BaseModel):
    """Target-owned declarative reaction to a live battlefield/environment context."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    context_id: EnvironmentContextId
    disadvantage_on: list[EnvironmentContextRollKind] = Field(default_factory=list)
    start_turn_damage_amount: int = Field(default=0, ge=0, le=200, exclude_if=lambda amount: amount == 0)
    start_turn_damage_type: DamageType | None = Field(default=None, exclude_if=lambda kind: kind is None)

    @model_validator(mode="after")
    def validate_reaction(self) -> "EnvironmentContextReaction":
        try:
            if any(not item.strip() for item in (self.source_id, self.source_name)):
                raise ValueError("Environment context reactions require a source id and name.")
            if bool(self.start_turn_damage_amount) != bool(self.start_turn_damage_type):
                raise ValueError("Environment-triggered damage requires both amount and type.")
            if not self.disadvantage_on and not self.start_turn_damage_amount:
                raise ValueError("Environment context reaction requires a roll penalty or damage.")
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
