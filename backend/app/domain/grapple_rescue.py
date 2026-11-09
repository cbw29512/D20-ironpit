"""Generic source-owned third-party grapple rescue rule; no runtime-name dispatch."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.action_types import AbilityName, ActionCost


class GrappleRescueRule(BaseModel):
    source_action_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    check_ability: AbilityName
    check_dc: int = Field(ge=1, le=40)
    helper_range_ft: int = Field(ge=0, le=120)
    action_cost: ActionCost = "action"
