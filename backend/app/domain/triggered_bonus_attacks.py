from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TriggeredBonusAttack(BaseModel):
    """A source-defined Bonus Action attack unlocked by a prior event this turn."""

    id: str
    name: str
    trigger: Literal["damage_target_already_bloodied"]
    attack_id: str
    resource_id: str
    resource_cost: int = Field(default=1, ge=1, le=20)
