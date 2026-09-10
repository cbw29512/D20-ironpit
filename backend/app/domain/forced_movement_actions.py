from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ForcedMovementAction(BaseModel):
    """A no-roll action that moves qualifying targets relative to the acting creature."""

    id: str
    name: str
    direction: Literal["toward_source", "away_from_source"]
    distance_ft: int = Field(ge=5, le=120, multiple_of=5)
    target_mode: Literal["creatures_grappled_by_self"]
    animation: str = "forced-movement"
