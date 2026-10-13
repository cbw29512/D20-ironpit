from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TurnStartSaveReaction(BaseModel):
    """Source-configured reaction when another creature begins its turn."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    trigger: Literal["other_creature_turn_start"] = "other_creature_turn_start"
    range_ft: int = Field(ge=5, le=600)
    source_must_see_target: bool = True
    target_must_see_source: bool = True
    save_ability: Literal[
        "strength", "dexterity", "constitution",
        "intelligence", "wisdom", "charisma",
    ]
    save_dc: int = Field(ge=1, le=40)
    failure_condition: Literal["frightened"] = "frightened"
    expires_at: Literal["target_turn_end"] = "target_turn_end"

