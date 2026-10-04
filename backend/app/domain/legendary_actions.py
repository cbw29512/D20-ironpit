from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LegendaryActionOption(BaseModel):
    """One printed legendary action that spends the shared after-turn pool."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    cost: int = Field(default=1, ge=1, le=6)
    kind: Literal["attack"] = "attack"
    attack_id: str = Field(min_length=1)
