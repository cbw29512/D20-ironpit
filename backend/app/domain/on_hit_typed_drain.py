"""Declarative on-hit typed damage transfer, independent of source ability name."""
from __future__ import annotations

import logging
from pydantic import BaseModel, ConfigDict

from app.domain.targeting import TargetQualification
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class OnHitTypedDrain(BaseModel):
    """Source parameters: one typed component funds reduction and self-healing."""

    model_config = ConfigDict(extra="forbid")
    damage_type: DamageType
    reduce_target_maximum_hp: bool = True
    heal_attacker: bool = True
    zero_maximum_hp_kills: bool = True


# Compatibility alias: existing attack definitions use the historical name.
AttackTargetQualification = TargetQualification

