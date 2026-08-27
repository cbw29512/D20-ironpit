from __future__ import annotations

from pydantic import BaseModel, Field


class MultiattackDefinition(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    attack_count: int = Field(ge=2, le=10)
    allowed_attack_ids: list[str] = Field(min_length=1)
    replacement_save_action_ids: list[str] = Field(default_factory=list)
    max_save_replacements: int = Field(default=0, ge=0, le=10)
