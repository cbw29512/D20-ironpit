from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import ActionCost


class InvisibilityAction(BaseModel):
    id: str = "invisibility"
    name: str = "Invisibility"
    action_cost: ActionCost = "action"
    concentration: bool = True
    ends_on_attack: bool = True
    ends_on_spell: bool = True
    ends_on_action_ids: list[str] = Field(default_factory=list)
