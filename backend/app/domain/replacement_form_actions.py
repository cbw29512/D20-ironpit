from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReplacementFormAction(BaseModel):
    """Declarative temporary-form action resolved by the shared replacement-form engine."""

    id: str
    name: str
    action_cost: Literal["action", "bonus_action"]
    form_template_id: str
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1)
    voluntary_revert_action: Literal["action", "bonus_action"] = "bonus_action"
    retain_spellcasting: bool = False
    source: str
