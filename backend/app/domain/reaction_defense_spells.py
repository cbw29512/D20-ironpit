"""Source-parameterized reaction AC and auto-hit protection.

State is fight-local: ordinary spell-slot resources and an expiring armor-class
modifier. Spell identity is descriptive; the engine dispatches on trigger data.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ReactionDefenseSpell(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    minimum_slot_level: int = Field(ge=1, le=9)
    ac_bonus: int = Field(gt=0, le=20)
    blocked_auto_hit_spell_ids: list[str] = Field(default_factory=list)
    duration: str = "source-turn-start"
