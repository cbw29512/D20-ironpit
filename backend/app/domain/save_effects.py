from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

SaveEffectTiming = Literal[
    "source_turn_start",
    "source_turn_end",
    "target_turn_start",
    "target_turn_end",
]


class FailedSaveTimedEffect(BaseModel):
    """Source-neutral timed rider applied only after a failed saving throw."""

    effect_id: str
    expiry_timing: SaveEffectTiming = "target_turn_end"
    next_attack_disadvantage: bool = False
