from __future__ import annotations

from pydantic import BaseModel

from app.domain.damage_types import DamageType


class DamageTakenDisadvantageRule(BaseModel):
    """Self debuff triggered by actually taking a matching damage type."""

    id: str
    name: str
    damage_type: DamageType
    attack_roll_disadvantage: bool = True
    ability_check_disadvantage: bool = True
