from __future__ import annotations

from pydantic import BaseModel, Field


class SelfBuffAction(BaseModel):
    id: str
    name: str
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)
    duration_source_turns: int = Field(default=1, ge=1, le=20)
    armor_class_bonus: int = 0
    save_advantage_abilities: list[str] = Field(default_factory=list)
    bonus_action_attack_id: str | None = None
