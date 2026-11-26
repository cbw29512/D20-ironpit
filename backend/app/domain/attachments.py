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
    damage_dice_count: int = 0
    damage_dice_size: int = 6
    damage_type: str | None = None
    periodic_effect_kind: str | None = None
    source_name: str = "Attachment"
    damage_bonus: int = 0
    damage_timing: str = "source_turn_start"
    detach_after_hp_lost: int | None = None
    actual_hp_lost: int = 0
    blocks_source_attacks: bool = False
    action_removable: bool = False
    action_removal_range_ft: int = 5
    source_detach_movement_ft: int = 0
    source_target_lock: bool = False
    source_advantage_against_target: bool = False
    source_speed_zero: bool = False
    moves_with_target: bool = False
    blinds_target: bool = False
    prevents_breathing: bool = False
    action_removal_check_ability: str | None = None
    action_removal_check_dc: int | None = None

    def __post_init__(self) -> None:
        try:
            if not all(isinstance(s, str) and s for s in (
                self.source_id, self.target_id, self.effect_id,
            )):
                raise ValueError("Attachment requires source, target, and effect identities.")
            if not isinstance(self.source_name, str) or not self.source_name:
                raise ValueError("Attachment requires printed source ability name.")
            if self.source_id == self.target_id:
                raise ValueError("Attachment source and target must differ.")
            if type(self.damage_dice_count) is not int or self.damage_dice_count < 0:
                raise ValueError("Attachment periodic dice count cannot be negative.")
            if type(self.damage_dice_size) is not int or self.damage_dice_size < 2:
                raise ValueError("Attachment requires valid periodic die size.")
            if self.periodic_effect_kind not in {None, "direct_hp_loss", "typed_damage"}:
                raise ValueError("Unsupported attachment periodic effect kind.")
            if (self.periodic_effect_kind is None) != (self.damage_dice_count == 0):
                raise ValueError("Only a non-periodic attachment may omit periodic dice.")
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
            if type(self.blocks_source_attacks) is not bool or type(self.action_removable) is not bool:
                raise ValueError("Attachment source controls must be booleans.")
            controls = (self.source_target_lock, self.source_advantage_against_target,
                        self.source_speed_zero, self.moves_with_target,
                        self.blinds_target, self.prevents_breathing)
            if any(type(value) is not bool for value in controls):
                raise ValueError("Attachment relationship controls must be booleans.")
            if (self.action_removal_check_ability is None) != (self.action_removal_check_dc is None):
                raise ValueError("Attachment removal check requires ability and DC together.")
            for cost in (self.action_removal_range_ft, self.source_detach_movement_ft):
                if type(cost) is not int or cost < 0 or cost % 5:
                    raise ValueError("Attachment removal range/cost must use nonnegative 5-ft steps.")
            if type(self.actual_hp_lost) is not int or self.actual_hp_lost < 0:
                raise ValueError("Recorded actual HP loss must be nonnegative.")
        except Exception:
            logger.exception("Invalid attachment state for source %s / effect %s.",
                             self.source_id, self.effect_id)
            raise
