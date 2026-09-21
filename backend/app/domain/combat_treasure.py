from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


CombatTreasureSlot = Literal["offense", "defense", "consumable", "accessory"]
CombatTreasureEffect = Literal[
    "weapon-enhancement", "spell-focus", "armor-class", "healing-potion",
    "saving-throws", "initiative", "speed", "max-hp",
]


class CombatTreasureAward(BaseModel):
    """One persistent combat-only treasure result gained before a canonical level."""

    level: int = Field(ge=2, le=20)
    roll: int = Field(ge=1, le=100)
    slot: CombatTreasureSlot
    effect: CombatTreasureEffect
    name: str
    bonus: int = Field(ge=1, le=5)
    target_id: str | None = None
    source: str = "Iron Pit combat treasure house rule"
