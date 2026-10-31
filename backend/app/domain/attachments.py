"""Immutable typed attachment record held only by fresh fight-local encounter state."""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Attachment:
    source_id: str
    target_id: str
    effect_id: str
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str | None
    periodic_effect_kind: str
    damage_bonus: int = 0
    damage_timing: str = "source_turn_start"
    detach_after_hp_lost: int | None = None
    actual_hp_lost: int = 0

    def __post_init__(self) -> None:
        try:
            if not all(isinstance(s, str) and s for s in (
                self.source_id, self.target_id, self.effect_id,
            )):
                raise ValueError("Attachment requires source, target, and effect identities.")
            if self.source_id == self.target_id:
                raise ValueError("Attachment source and target must differ.")
            if type(self.damage_dice_count) is not int or self.damage_dice_count <= 0:
                raise ValueError("Attachment requires positive periodic dice count.")
            if type(self.damage_dice_size) is not int or self.damage_dice_size < 2:
                raise ValueError("Attachment requires valid periodic die size.")
            if self.periodic_effect_kind not in {"direct_hp_loss", "typed_damage"}:
                raise ValueError("Unsupported attachment periodic effect kind.")
            if self.periodic_effect_kind == "direct_hp_loss" and self.damage_type is not None:
                raise ValueError("Direct HP loss must not have a damage type.")
            if self.periodic_effect_kind == "typed_damage" and not self.damage_type:
                raise ValueError("Typed attachment damage requires its damage type.")
            if type(self.damage_bonus) is not int:
                raise ValueError("Periodic effect bonus must be an integer.")
            if self.damage_timing not in {
                "source_turn_start", "target_turn_start", "target_turn_end",
            }:
                raise ValueError("Unsupported attachment damage timing.")
            if self.detach_after_hp_lost is not None and (
                type(self.detach_after_hp_lost) is not int or self.detach_after_hp_lost <= 0
            ):
                raise ValueError("Detach threshold must be a positive integer.")
            if type(self.actual_hp_lost) is not int or self.actual_hp_lost < 0:
                raise ValueError("Recorded actual HP loss must be nonnegative.")
        except Exception:
            logger.exception("Invalid attachment state for source %s / effect %s.",
                             self.source_id, self.effect_id)
            raise
