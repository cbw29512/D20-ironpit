from __future__ import annotations

from pydantic import BaseModel, Field


class MovementModes(BaseModel):
    """Complete movement fingerprint retained from a creature stat block."""

    walk_ft: int = Field(ge=0)
    fly_ft: int = Field(default=0, ge=0)
    climb_ft: int = Field(default=0, ge=0)
    swim_ft: int = Field(default=0, ge=0)
    burrow_ft: int = Field(default=0, ge=0)
    hover: bool = False
