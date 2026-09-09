from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HealingEffectIR(BaseModel):
    kind: Literal["healing"] = "healing"
    dice_count: int = Field(default=0, ge=0, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    bonus: int = Field(default=0, ge=0)
