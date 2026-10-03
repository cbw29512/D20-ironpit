from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models import ConditionName


class FriendlyConditionImmunityAuraGrant(BaseModel):
    """Passive ally aura that suppresses one named condition while eligible."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    radius_ft: int = Field(ge=0, le=120)
    condition_id: ConditionName
    inactive_while_incapacitated: bool = False
    inactive_while_unconscious: bool = False
