"""Declarative multi-hit threshold that upgrades a source-owned grapple.

The attack/action name is solely a display label; semantics are source-independent.
No encounter state may be stored on this immutable rule.
"""
from __future__ import annotations

import logging
from pydantic import BaseModel, ConfigDict, Field
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


class MultiHitGrappleEffect(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_name: str = Field(min_length=1)
    effect_id: str = Field(min_length=1)
    standalone_action: bool = False
    attack_id: str = Field(min_length=1)
    hits_required: int = Field(ge=2, le=8)
    max_target_size: CreatureSize
    escape_dc: int = Field(ge=1, le=40)
    range_ft: int = Field(ge=0)
    max_active_grapples: int = Field(ge=1, le=20)
    restrains: bool = True
    blinds: bool = True
    prevents_breathing: bool = True
