from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName, DamageTypeName
from app.domain.size import CreatureSize


class BreakableRestraint(BaseModel):
    """Immutable on-hit restraint rules with an escape check and breakable object."""

    condition_id: ConditionName = "restrained"
    max_target_size: CreatureSize | None = None
    escape_ability: AbilityName
    escape_dc: int = Field(ge=1, le=40)
    object_ac: int = Field(ge=1, le=40)
    object_hp: int = Field(ge=1, le=1000)
    damage_vulnerabilities: list[DamageTypeName] = Field(default_factory=list)
    damage_immunities: list[DamageTypeName] = Field(default_factory=list)


class RestraintState(BaseModel):
    """Temporary combat state created when a breakable restraint lands."""

    source_id: str
    source_effect_id: str
    condition_id: ConditionName
    escape_ability: AbilityName
    escape_dc: int = Field(ge=1, le=40)
    object_ac: int = Field(ge=1, le=40)
    current_hp: int = Field(ge=0)
    max_hp: int = Field(ge=1)
    damage_vulnerabilities: list[DamageTypeName] = Field(default_factory=list)
    damage_immunities: list[DamageTypeName] = Field(default_factory=list)
