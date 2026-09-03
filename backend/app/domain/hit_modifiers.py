from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HitModifierEffect(BaseModel):
    """Source-neutral modifier applied automatically after a successful hit."""

    kind: Literal["attacks-against-advantage"]
    consume_on_attack_against: bool = False
    expires_at_start_of_source_turn: bool = False
