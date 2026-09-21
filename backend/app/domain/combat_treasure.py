from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


CombatTreasureSlot = Literal["offense", "defense", "focus", "accessory", "resource"]
CombatTreasureEffect = Literal[
    "weapon-enhancement", "armor-class", "spell-focus", "saving-throws",
    "initiative", "speed", "max-hp", "resource-use",
]


class CombatTreasureAward(BaseModel):
    """One recorded Iron Pit combat-only treasure result for a canonical pregen level."""

    level: int = Field(ge=2, le=20)
    chance_roll: int = Field(ge=1, le=100)
    table_roll: int = Field(ge=1, le=20)
    slot: CombatTreasureSlot
    effect: CombatTreasureEffect
    name: str
    bonus: int = Field(ge=1, le=3)
    target_id: str | None = None
    source: str = "Iron Pit combat treasure house rule"
