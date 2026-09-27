from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import ActionCost
from app.domain.save_damage import DamageTypeName


class AutoHitSpellAction(BaseModel):
    """A deterministic spell that deals projectile damage without an attack roll or save."""

    id: str
    name: str
    level: int = Field(ge=1, le=9)
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    projectile_count: int = Field(ge=1, le=20)
    projectiles_per_slot_above: int = Field(default=0, ge=0, le=20)
    damage_dice_count: int = Field(default=1, ge=0, le=20)
    damage_dice_size: int = Field(default=4, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName
    animation: str = "spell-projectile"
    source: str | None = None
