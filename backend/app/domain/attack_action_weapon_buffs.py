from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons_base import DamageType


class AttackActionWeaponBuff(BaseModel):
    """Source-neutral weapon buff activated when the combatant takes the Attack action."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1, le=20)
    weapon_id: str = Field(min_length=1)
    duration_rounds: int = Field(ge=1, le=600)
    attack_roll_bonus: int = Field(default=0, ge=0, le=20)
    damage_type_choice: DamageType | None = None
    source_is_magical: bool = True
    animation: str = "buff"
