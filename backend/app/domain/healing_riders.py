from __future__ import annotations

from pydantic import BaseModel, Field


class OutgoingHealingDiceMaximizer(BaseModel):
    """Source-owned rule that maximizes dice rolled by the source's healing actions."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
