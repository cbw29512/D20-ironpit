from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import ConditionTiming


class OnHitTimedEffect(BaseModel):
    """Source-neutral timed effect applied after a successful hit."""

    effect_id: str
    duration_rounds: int = Field(default=1, ge=1, le=14400)
    expiry_timing: ConditionTiming = "source_turn_start"
    suppress_action: bool = False
    suppress_bonus_action: bool = False
    suppress_reactions: bool = False
    suppress_movement: bool = False
    next_attack_disadvantage: bool = False
    source_is_magical: bool = True
