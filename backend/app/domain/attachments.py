from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class AttachmentEffectDefinition(BaseModel):
    """Declarative on-hit attachment with source-turn periodic damage."""

    kind: Literal["attachment"] = "attachment"
    periodic_damage_count: int = Field(ge=0, le=40)
    periodic_damage_size: int = Field(default=6, ge=2, le=100)
    periodic_damage_bonus: int = 0
    periodic_damage_type: DamageType
    timing: Literal["source_turn_start"] = "source_turn_start"
    forbids_source_attack_ids: list[str] = Field(default_factory=list)
    detachable_by_target_action: bool = True
    detachable_by_adjacent_action: bool = True


class AttachmentState(BaseModel):
    """Mutable source-target relationship created by an attachment effect."""

    source_id: str
    target_id: str
    source_effect_id: str
    applied_round: int = Field(ge=1)
    periodic_damage_count: int = Field(ge=0, le=40)
    periodic_damage_size: int = Field(default=6, ge=2, le=100)
    periodic_damage_bonus: int = 0
    periodic_damage_type: DamageType
    forbids_source_attack_ids: list[str] = Field(default_factory=list)
    detachable_by_target_action: bool = True
    detachable_by_adjacent_action: bool = True
