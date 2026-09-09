from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class RegenerationDefinition(BaseModel):
    id: str
    healing: int = Field(gt=0, le=1000)
    suppressed_by_damage_types: list[DamageType] = Field(default_factory=list)
    requires_positive_hp: bool = True
