from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import ActionCost


class ConcentrationRepeatSaveAction(BaseModel):
    """An Action that reuses a save spell's effect while its Concentration remains active."""

    id: str
    name: str
    source_spell_id: str
    action_cost: ActionCost = "action"
    priority: int = Field(default=50, ge=0, le=1000)
    animation: str = "spell-save"
    source: str
