from __future__ import annotations

from pydantic import BaseModel

from app.domain.actions import ConditionTiming


class FailedSaveTimedEffect(BaseModel):
    """Source-neutral timed rider applied only after a failed saving throw."""

    effect_id: str
    expiry_timing: ConditionTiming = "target_turn_end"
    next_attack_disadvantage: bool = False
