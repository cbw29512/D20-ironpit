from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize


class ParryReaction(BaseModel):
    """Standard SRD Parry: add AC against one triggering melee hit while armed."""

    ac_bonus: int = Field(ge=1, le=20)


class RedirectAttackReaction(BaseModel):
    """SRD Goblin Boss reaction: swap with a nearby Small/Medium ally targeted by the same roll."""

    ally_range_ft: int = Field(default=5, ge=1, le=30)
    ally_max_size: CreatureSize = CreatureSize.MEDIUM


class DamageReactionAttack(BaseModel):
    """Reusable reaction attack triggered after damage from a nearby creature.

    This is immutable template policy only. Runtime dispatch must separately prove
    that damage was applied, preserve the source creature, check authoritative
    distance, spend the Reaction, and resolve the selected attack immediately.
    """

    source_feature: str = Field(min_length=1)
    trigger: Literal["damaged-by-creature"] = "damaged-by-creature"
    source_range_ft: int = Field(default=5, ge=1, le=120)
    attack_kind: Literal["melee"] = "melee"
