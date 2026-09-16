from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import ConditionName


class ZeroHpSaveDamageRider(BaseModel):
    """A source-declared rider that applies only when save damage itself causes 0 HP."""

    stable: Literal[True] = True
    condition_ids: list[ConditionName] = Field(min_length=1)
    duration_rounds: int = Field(ge=1)
