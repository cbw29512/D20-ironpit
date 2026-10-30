from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator


class CombatModifierEffect(BaseModel):
    """Source-neutral modifier effect applied by an attack, save, spell, or feature."""

    kind: Literal["attacks-against-advantage", "next-attack-advantage", "next-attack-disadvantage", "speed"]
    flat_bonus: int = 0
    recipient: Literal["target", "source"] = "target"
    consume_on_attack_against: bool = False
    expires_at_start_of_source_turn: bool = False
    expires_at_end_of_source_turn: bool = False
    expires_at_end_of_current_turn: bool = False
    expires_at_end_of_target_turn: bool = False

    @model_validator(mode="after")
    def validate_payload(self) -> "CombatModifierEffect":
        if self.kind in {"attacks-against-advantage", "next-attack-advantage", "next-attack-disadvantage"} and self.flat_bonus:
            raise ValueError("Attack roll-mode modifiers do not accept a flat bonus.")
        if self.kind == "speed" and self.flat_bonus == 0:
            raise ValueError("Speed modifiers require a nonzero flat bonus.")
        if self.consume_on_attack_against and self.kind != "attacks-against-advantage":
            raise ValueError("Only attack-Advantage modifiers can be consumed by an attack against the target.")
        expiry_flags = (
            self.expires_at_start_of_source_turn,
            self.expires_at_end_of_source_turn,
            self.expires_at_end_of_current_turn,
            self.expires_at_end_of_target_turn,
        )
        if sum(bool(flag) for flag in expiry_flags) > 1:
            raise ValueError("Modifier expiry must declare only one lifecycle boundary.")
        return self


# Backward-compatible import name while attack-specific call sites migrate.
HitModifierEffect = CombatModifierEffect
