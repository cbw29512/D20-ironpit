from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ZeroHpReplacementEffectDefinition(BaseModel):
    """Declarative failed-save effect that replaces a later zero-HP outcome."""

    kind: Literal["zero-hp-replacement"] = "zero-hp-replacement"
    effect_id: str
    replacement_mode: Literal["source-template"] = "source-template"
    control_mode: Literal["source-side"] = "source-side"
    replacement_hp: int = Field(default=10, ge=1, le=999)


class ZeroHpReplacementState(BaseModel):
    """Mutable fight state for a source-owned pending zero-HP replacement."""

    effect_id: str
    source_id: str
    source_effect_id: str
    replacement_mode: Literal["source-template"] = "source-template"
    control_mode: Literal["source-side"] = "source-side"
    replacement_hp: int = Field(default=10, ge=1, le=999)


__all__ = ["ZeroHpReplacementEffectDefinition", "ZeroHpReplacementState"]
