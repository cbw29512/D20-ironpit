from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize


class ParryReaction(BaseModel):
    """Standard SRD Parry: add AC against one triggering melee hit while armed."""

    ac_bonus: int = Field(ge=1, le=20)


class RedirectAttackReaction(BaseModel):
    """SRD Goblin Boss reaction: swap with a nearby Small/Medium ally targeted by the same roll."""

    ally_range_ft: int = Field(default=5, ge=1, le=30)
    ally_max_size: CreatureSize = CreatureSize.MEDIUM
