"""Declarative on-hit typed damage transfer, independent of source ability name."""
from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class OnHitTypedDrain(BaseModel):
    """Source parameters: one typed component funds reduction and self-healing."""

    model_config = ConfigDict(extra="forbid")
    damage_type: DamageType
    reduce_target_maximum_hp: bool = True
    heal_attacker: bool = True
    zero_maximum_hp_kills: bool = True


class AttackTargetQualification(BaseModel):
    """Any declared status suffices; an unproved willingness is never assumed."""

    model_config = ConfigDict(extra="forbid")
    any_of: list[Literal[
        "source_grappled", "incapacitated", "restrained", "willing",
    ]] = Field(min_length=1)

