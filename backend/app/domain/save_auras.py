from __future__ import annotations

from pydantic import BaseModel, Field


class SaveAdvantageAura(BaseModel):
    id: str
    effect_id: str
    range_ft: int = Field(gt=0)
    includes_source: bool = True
    beneficiary_archetypes: list[str] = Field(default_factory=list)
