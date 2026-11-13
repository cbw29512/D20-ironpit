"""Generic source-owned third-party grapple rescue rule; no runtime-name dispatch."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.action_types import AbilityName, ActionCost


class GrappleRescueRule(BaseModel):
    source_action_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    check_ability: AbilityName
    check_dc: int = Field(ge=1, le=40)
    helper_range_ft: int = Field(ge=0, le=120)
    action_cost: ActionCost = "action"
    # Default preserves already-certified third-party owner-side rescue.
    allow_held_target: bool = False
    helper_range_anchor: Literal["owner", "held_target"] = "owner"
    requires_breakable_object: bool = False
    release_verb: Literal["pull", "break"] = "pull"
