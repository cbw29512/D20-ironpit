from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class MovementModes(BaseModel):
    """Complete movement fingerprint retained from a creature stat block."""

    walk_ft: int = Field(ge=0)
    fly_ft: int = Field(default=0, ge=0)
    climb_ft: int = Field(default=0, ge=0)
    swim_ft: int = Field(default=0, ge=0)
    burrow_ft: int = Field(default=0, ge=0)
    hover: bool = False


class MovementModeGrant(BaseModel):
    """Source-owned temporary movement mode granted by an active effect."""

    mode: Literal["fly", "climb", "swim", "burrow"]
    fixed_speed_ft: int | None = Field(default=None, ge=0)
    match_current_speed: bool = False

    @model_validator(mode="after")
    def validate_speed_source(self) -> "MovementModeGrant":
        if self.match_current_speed == (self.fixed_speed_ft is not None):
            raise ValueError("Movement-mode grant requires exactly one speed source.")
        return self
