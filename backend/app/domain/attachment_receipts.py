"""Source-neutral replay receipts for fight-local attachment changes."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class AttachmentChange(BaseModel):
    """One linked status transition; the combat-state relationship is authoritative."""

    operation: Literal["attach", "detach"]
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    effect_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
