from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MovementModes(BaseModel):
    """Complete movement fingerprint retained from a creature stat block."""

    walk_ft: int = Field(ge=0)
    fly_ft: int = Field(default=0, ge=0)
    climb_ft: int = Field(default=0, ge=0)
    swim_ft: int = Field(default=0, ge=0)
    burrow_ft: int = Field(default=0, ge=0)
    hover: bool = False


DifficultTerrainScope = Literal["all", "nonmagical"]


class DifficultTerrainBypassGrant(BaseModel):
    """Source-owned permission to ignore extra movement cost from matching difficult terrain."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    scope: DifficultTerrainScope
