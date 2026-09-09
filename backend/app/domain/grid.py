from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GridPosition(BaseModel):
    """Top-left occupied cell for a combatant footprint on the Iron Pit grid."""

    x: int = Field(ge=0)
    y: int = Field(ge=0)


class BattleMapDefinition(BaseModel):
    """Immutable tactical-map dimensions shared by every combat resolver."""

    id: str = Field(min_length=1)
    width_squares: int = Field(ge=1)
    height_squares: int = Field(ge=1)
    cell_size_ft: Literal[5] = 5
