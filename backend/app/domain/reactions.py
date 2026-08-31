from __future__ import annotations

from pydantic import BaseModel, Field


class ParryReaction(BaseModel):
    """Standard SRD Parry: add AC against one triggering melee hit while armed."""

    ac_bonus: int = Field(ge=1, le=20)
