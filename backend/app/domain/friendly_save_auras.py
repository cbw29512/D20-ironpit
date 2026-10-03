from __future__ import annotations

from pydantic import BaseModel, Field


class FriendlySavingThrowAuraGrant(BaseModel):
    """Passive ally aura that grants a flat bonus to saving throws."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    radius_ft: int = Field(ge=0, le=120)
    flat_bonus: int = Field(ge=1, le=20)
    non_stacking_group: str | None = Field(default=None, min_length=1)
    inactive_while_incapacitated: bool = False
    inactive_while_unconscious: bool = False
