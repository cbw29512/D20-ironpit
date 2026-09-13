from __future__ import annotations

from pydantic import BaseModel, Field


class ZeroHpPrevention(BaseModel):
    resource_id: str
    max_trigger_damage: int = Field(ge=0)
    resulting_hp: int = Field(default=1, ge=1)
