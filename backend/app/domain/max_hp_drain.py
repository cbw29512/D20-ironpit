from __future__ import annotations

from pydantic import BaseModel

from app.domain.weapons import DamageType


class MaxHpDrainEffect(BaseModel):
    """Declarative on-hit maximum-HP drain driven by applied damage of one type."""

    damage_type: DamageType
    heal_attacker: bool = False
    zero_max_hp_kills: bool = True
