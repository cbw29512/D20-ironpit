from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize
from app.domain.weapons import DamageType


class ParryReaction(BaseModel):
    """Standard SRD Parry: add AC against one triggering melee hit while armed."""

    ac_bonus: int = Field(ge=1, le=20)


class RedirectAttackReaction(BaseModel):
    """SRD Goblin Boss reaction: swap with a nearby Small/Medium ally targeted by the same roll."""

    ally_range_ft: int = Field(default=5, ge=1, le=30)
    ally_max_size: CreatureSize = CreatureSize.MEDIUM


class ProjectileCatchReaction(BaseModel):
    """Catch an incoming ranged projectile after a hit and negate matching damage on a successful save."""

    save_ability: Literal["dexterity"] = "dexterity"
    save_dc: int = Field(default=10, ge=1, le=40)
    damage_type: DamageType = DamageType.BLUDGEONING


class SpellReflectionReaction(BaseModel):
    """Retarget a failed spell attack or successfully saved spell to another visible combatant."""

    range_ft: int = Field(default=30, ge=1, le=120)
