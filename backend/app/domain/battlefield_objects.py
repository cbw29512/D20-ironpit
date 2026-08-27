from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.conditions import ConditionType
from app.domain.damage_types import DamageType


class BattlefieldObjectDefinition(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    armor_class: int = Field(ge=1, le=40)
    max_hp: int = Field(ge=1)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)


class BattlefieldObjectState(BaseModel):
    instance_id: str = Field(min_length=1)
    definition: BattlefieldObjectDefinition
    source_id: str
    target_id: str | None = None
    linked_condition: ConditionType | None = None
    current_hp: int = Field(ge=0)
    is_destroyed: bool = False
