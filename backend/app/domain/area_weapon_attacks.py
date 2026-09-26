from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.targeting import AreaTargeting


class AreaWeaponAttackAction(BaseModel):
    """One Action that makes a separate weapon attack against each chosen area target."""

    id: str
    name: str
    attack_id: str
    range_ft: int = Field(ge=5)
    area: AreaTargeting
    action_cost: str = "action"
    source: str | None = None
