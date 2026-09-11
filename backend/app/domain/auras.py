from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class EndTurnDamageAura(BaseModel):
    """Source-neutral damaging emanation resolved at the end of the owner's turn."""

    id: str
    name: str
    radius_ft: int = Field(gt=0)
    damage_dice_count: int = Field(ge=0)
    damage_dice_size: int = Field(ge=1)
    damage_bonus: int = 0
    damage_type: DamageType
    disabled_while_incapacitated: bool = False
