from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.combatants import CombatantTemplate


class ReplacementFormState(BaseModel):
    """Runtime state for a temporary replacement form such as Wild Shape.

    The original combatant template remains authoritative for identity/resources.
    The active form template supplies temporary physical combat statistics.
    """

    source_id: str
    source_name: str
    original_template: CombatantTemplate
    form_template: CombatantTemplate
    original_hp: int = Field(ge=0)
    form_hp: int = Field(ge=0)
    form_max_hp: int = Field(ge=1)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1)
    voluntary_revert_action: str = "bonus_action"
