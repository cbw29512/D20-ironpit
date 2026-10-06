from __future__ import annotations

from pydantic import BaseModel

from app.domain.weapons import DamageType


class DamageAbsorptionRule(BaseModel):
    """Replace matching typed damage with equal ordinary healing."""

    source_id: str
    source_name: str
    damage_type: DamageType
