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
    damage_type: str | None
    periodic_effect_kind: str
    damage_bonus: int = 0
    damage_timing: str = "source_turn_start"
    detach_after_hp_lost: int | None = None
    actual_hp_lost: int = 0

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id or not self.effect_id:
            raise ValueError("Attachment requires source, target, and effect identities.")
        if self.source_id == self.target_id:
            raise ValueError("Attachment source and target must differ.")
        if self.damage_dice_count <= 0 or self.damage_dice_size < 2:
            raise ValueError("Attachment requires valid damage dice.")
        if self.periodic_effect_kind not in {"direct_hp_loss", "typed_damage"}:
            raise ValueError("Unsupported attachment periodic effect kind.")
        if self.periodic_effect_kind == "direct_hp_loss" and self.damage_type is not None:
            raise ValueError("Direct HP loss must not be typed damage.")
        if self.periodic_effect_kind == "typed_damage" and not self.damage_type:
            raise ValueError("Typed attachment damage requires a damage type.")
        if type(self.damage_bonus) is not int:
            raise ValueError("Periodic effect bonus must be an integer.")
        if self.damage_timing not in {"source_turn_start", "target_turn_start", "target_turn_end"}:
            raise ValueError("Unsupported attachment damage timing.")
        if self.detach_after_hp_lost is not None and self.detach_damage_total <= 0:
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


def record_attachment_hp_loss(
    existing: tuple[Attachment, ...], source_id: str,
    effect_id: str, actual_hp_lost: int,
) -> tuple[Attachment, ...]:
    """Count actual periodic HP loss, not opening-hit damage or raw dice."""
    try:
        if type(actual_hp_lost) is not int or actual_hp_lost < 0:
            raise ValueError("Actual HP lost must be a nonnegative integer.")
        result = []
        for row in existing:
            if row.source_id != source_id or row.effect_id != effect_id:
                result.append(row)
                continue
            total = row.actual_hp_lost + actual_hp_lost
            if row.detach_damage_total is None or total < row.detach_damage_total:
                result.append(replace(row, actual_hp_lost=total))
        return tuple(result)
    except Exception:
        logger.exception("Attachment HP-loss ledger failed for %s / %s.", source_id, effect_id)
        raise


@dataclass(frozen=True)
class LinkedEffect:
    """One visible side of an attachment relationship; source ownership is explicit."""
    owner_id: str
    counterpart_id: str
    effect_id: str
    kind: str


def linked_attachment_effects(
    existing: tuple[Attachment, ...],
) -> tuple[LinkedEffect, ...]:
    """Project each relationship into a victim debuff and source buff.

    The attachment ledger remains authoritative: detaching removes both
    projections without leaving independent orphaned timed effects.
    """
    try:
        effects: list[LinkedEffect] = []
        for row in existing:
            effects.extend((
                LinkedEffect(
                    owner_id=row.target_id,
                    counterpart_id=row.source_id,
                    effect_id="attached",
                    kind="debuff",
                ),
                LinkedEffect(
                    owner_id=row.source_id,
                    counterpart_id=row.target_id,
                    effect_id=row.effect_id,
                    kind="buff",
                ),
            ))
        return tuple(effects)
    except Exception:
        logger.exception("Failed to project linked attachment buffs and debuffs.")
        raise


def active_attachment_target(
    existing: tuple[Attachment, ...],
    source_id: str, effect_id: str,
) -> str | None:
    """Resolve the current target of an attachment-owned automatic effect."""
    try:
        matches = [
            row.target_id for row in existing
            if row.source_id == source_id and row.effect_id == effect_id
        ]
        if len(matches) > 1:
            raise ValueError("Attachment owner has multiple targets for one effect.")
        return matches[0] if matches else None
    except Exception:
        logger.exception("Failed to resolve attachment target for %s.", source_id)
        raise
