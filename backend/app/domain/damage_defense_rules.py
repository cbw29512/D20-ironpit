from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class ConditionalDamageResistance(BaseModel):
    """Resistance that applies only when declarative attack-source qualifiers match."""

    damage_types: list[DamageType] = Field(min_length=1)
    nonmagical_attack_only: bool = False
    bypass_if_silvered: bool = False
    bypass_if_adamantine: bool = False
