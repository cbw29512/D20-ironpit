from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.domain.weapons_base import DamageType


class DamageSourceQualifier(StrEnum):
    ATTACK = "attack"
    WEAPON = "weapon"
    MELEE = "melee"
    RANGED = "ranged"
    MAGICAL = "magical"


class DamageDefenseKind(StrEnum):
    RESISTANCE = "resistance"
    IMMUNITY = "immunity"
    VULNERABILITY = "vulnerability"


class ConditionalDamageDefense(BaseModel):
    """Generic defense matched against damage type plus source semantics."""

    id: str
    kind: DamageDefenseKind
    damage_types: list[DamageType] = Field(min_length=1)
    required_source_qualifiers: list[DamageSourceQualifier] = Field(default_factory=list)
    forbidden_source_qualifiers: list[DamageSourceQualifier] = Field(default_factory=list)
