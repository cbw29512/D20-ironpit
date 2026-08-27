from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GrantedAction(BaseModel):
    """A verified feature that permits a base action at a different action cost."""

    id: str = Field(min_length=1)
    action_id: Literal["disengage", "hide"]
    action_cost: Literal["action", "bonus_action"]
