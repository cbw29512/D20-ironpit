from __future__ import annotations

from pydantic import BaseModel


class MaxHpDrainEffect(BaseModel):
    """Declarative on-hit maximum-HP drain driven by one applied damage type."""

    damage_type: str
    heal_attacker: bool = False
    zero_max_hp_kills: bool = True
