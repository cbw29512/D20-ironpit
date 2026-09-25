from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DamageTypeName = Literal[
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
]


class SaveDamageComponent(BaseModel):
    """One independently typed damage component controlled by a shared saving throw."""

    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName
