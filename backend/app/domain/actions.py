from __future__ import annotations

from pydantic import BaseModel, Field


class AttackActionSlot(BaseModel):
    """One attack granted by an Attack action; listed IDs are legal choices for the slot."""

    attack_ids: list[str] = Field(min_length=1, max_length=16)


class AttackActionDefinition(BaseModel):
    """The attack rolls a combatant can make when it takes its preferred Attack action."""

    id: str
    name: str
    slots: list[AttackActionSlot] = Field(min_length=2, max_length=8)
