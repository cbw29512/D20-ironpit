from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator


class HitModifierEffect(BaseModel):
    """Source-neutral modifier applied automatically after a successful hit."""

    kind: Literal["attacks-against-advantage", "next-attack-disadvantage", "speed"]
    flat_bonus: int = 0
    consume_on_attack_against: bool = False
    expires_at_start_of_source_turn: bool = False
    expires_at_end_of_target_turn: bool = False

    @model_validator(mode="after")
    def validate_payload(self) -> "HitModifierEffect":
        if self.kind in {"attacks-against-advantage", "next-attack-disadvantage"} and self.flat_bonus:
            raise ValueError("Attack roll-mode hit modifiers do not accept a flat bonus.")
        if self.kind == "speed" and self.flat_bonus == 0:
            raise ValueError("Speed hit modifiers require a nonzero flat bonus.")
        if self.consume_on_attack_against and self.kind != "attacks-against-advantage":
            raise ValueError("Only attack-Advantage hit modifiers can be consumed by an attack against the target.")
        if self.expires_at_start_of_source_turn and self.expires_at_end_of_target_turn:
            raise ValueError("Hit modifier expiry must be source-relative or target-relative, not both.")
        return self
