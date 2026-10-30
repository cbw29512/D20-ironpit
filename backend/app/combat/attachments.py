"""Universal owner-target attachment lifecycle, without Grappled or speed penalties."""
from __future__ import annotations

import logging
from dataclasses import dataclass, replace

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Attachment:
    source_id: str
    target_id: str
    effect_id: str
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str
    damage_timing: str = "source_turn_start"
    detach_damage_total: int | None = None
    accumulated_damage: int = 0

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id or not self.effect_id:
            raise ValueError("Attachment requires source, target, and effect identities.")
        if self.source_id == self.target_id:
            raise ValueError("Attachment source and target must differ.")
        if self.damage_dice_count <= 0 or self.damage_dice_size < 2:
            raise ValueError("Attachment requires valid damage dice.")
        if self.damage_timing not in {"source_turn_start", "target_turn_start", "target_turn_end"}:
            raise ValueError("Unsupported attachment damage timing.")
        if self.detach_damage_total is not None and self.detach_damage_total <= 0:
            raise ValueError("Detach threshold must be positive.")


def attach(
    existing: tuple[Attachment, ...], attachment: Attachment,
) -> tuple[Attachment, ...]:
    """Add an owner-target link; do not apply the Grappled condition."""
    try:
        if any(
            row.source_id == attachment.source_id and row.effect_id == attachment.effect_id
            for row in existing
        ):
            raise ValueError("Source already has this attachment active.")
        return (*existing, attachment)
    except Exception:
        logger.exception("Unable to attach source %s to target %s.", attachment.source_id, attachment.target_id)
        raise


def detach_for_combatant(
    existing: tuple[Attachment, ...], combatant_id: str,
) -> tuple[Attachment, ...]:
    """Cleanup when either the source or target dies or leaves combat."""
    try:
        return tuple(row for row in existing if combatant_id not in {row.source_id, row.target_id})
    except Exception:
        logger.exception("Attachment cleanup failed for %s.", combatant_id)
        raise


def record_attachment_damage(
    existing: tuple[Attachment, ...], source_id: str,
    effect_id: str, damage: int,
) -> tuple[Attachment, ...]:
    """Track actual damage for source-defined auto-detach thresholds."""
    try:
        if type(damage) is not int or damage < 0:
            raise ValueError("Attachment damage must be a nonnegative integer.")
        result = []
        for row in existing:
            if row.source_id != source_id or row.effect_id != effect_id:
                result.append(row)
                continue
            total = row.accumulated_damage + damage
            if row.detach_damage_total is None or total < row.detach_damage_total:
                result.append(replace(row, accumulated_damage=total))
        return tuple(result)
    except Exception:
        logger.exception("Attachment damage ledger failed for %s / %s.", source_id, effect_id)
        raise
