from __future__ import annotations

from pydantic import BaseModel, Field


class VisualLoadout(BaseModel):
    """Immutable visual metadata carried by a combatant template."""

    armor: str
    main_hand: str
    off_hand: str | None = None
    body_style: str = "humanoid"


class ResourceDefinition(BaseModel):
    """Declarative finite resource schema shared by heroes and monsters."""

    id: str
    name: str
    max_uses: int = Field(ge=0)
