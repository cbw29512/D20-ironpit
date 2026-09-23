from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.weapons_base import DamageType


class QualifiedDamageDefense(BaseModel):
    """Declarative defense that applies only when its source predicates match."""

    kind: Literal["resistance", "immunity", "vulnerability"]
    damage_types: list[DamageType] = Field(min_length=1)
    attack_only: bool = False
    magical: bool | None = None
    bypass_materials: list[str] = Field(default_factory=list)
    source_name: str
    source_text: str
