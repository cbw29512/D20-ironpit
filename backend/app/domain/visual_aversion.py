"""Typed fight-local source-scoped visual aversion windows."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VisualAversionWindow(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    observer_id: str = Field(min_length=1)
    source_combatant_id: str = Field(min_length=1)
    expires_on_observer_turn_start: int = Field(ge=0)
