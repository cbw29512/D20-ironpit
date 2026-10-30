from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize


class ParryReaction(BaseModel):
    """AC reaction that can optionally counterattack when it converts a hit to a miss."""

    ac_bonus: int = Field(ge=1, le=20)
    source_feature: str = "parry"
    counterattack_attack_id: str | None = None
    counterattack_range_ft: int = Field(default=5, ge=1, le=30)


class RedirectAttackReaction(BaseModel):
    """SRD Goblin Boss reaction: swap with a nearby Small/Medium ally targeted by the same roll."""

    ally_range_ft: int = Field(default=5, ge=1, le=30)
    ally_max_size: CreatureSize = CreatureSize.MEDIUM
