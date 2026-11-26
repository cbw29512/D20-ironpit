"""Universal owner-target attachment lifecycle, without Grappled or speed penalties."""
from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from app.domain.attachments import Attachment

logger = logging.getLogger(__name__)


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



def detach_link(
    existing: tuple[Attachment, ...], source_id: str, effect_id: str,
) -> tuple[Attachment, ...]:
    """Remove exactly one owned link after the caller validates Action/movement cost."""
    try:
        return tuple(row for row in existing
                     if (row.source_id, row.effect_id) != (source_id, effect_id))
    except Exception:
        logger.exception("Failed to detach source %s effect %s.", source_id, effect_id)
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
            if row.detach_after_hp_lost is None or total < row.detach_after_hp_lost:
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


def sync_attachment_controls(setup) -> None:
    """Rebuild fight-local linked controls from the authoritative attachment ledger."""
    try:
        members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
        for member in members.values():
            state = member.state
            prior_blind = bool(state.attachment_blind_source_ids)
            blind = [row.source_id for row in setup.attachments
                     if row.target_id == member.combatant_id and row.blinds_target]
            breath = [row.source_id for row in setup.attachments
                      if row.target_id == member.combatant_id and row.prevents_breathing]
            speed = [row.effect_id for row in setup.attachments
                     if row.source_id == member.combatant_id and row.source_speed_zero]
            if blind and not prior_blind:
                state.attachment_blind_preexisting = "blinded" in state.active_effect_ids
            state.attachment_blind_source_ids = blind
            state.attachment_breathing_source_ids = breath
            state.attachment_speed_zero_source_ids = speed
            if blind and "blinded" not in state.active_effect_ids:
                state.active_effect_ids.append("blinded")
            if prior_blind and not blind:
                other_blind = (
                    state.attachment_blind_preexisting
                    or any(source.blinds for source in state.grapple_sources)
                    or any(effect.effect_id == "blinded" for effect in state.timed_effects)
                    or "blinded" in state.template.innate_condition_ids
                )
                if not other_blind:
                    state.active_effect_ids = [item for item in state.active_effect_ids
                                               if item != "blinded"]
                state.attachment_blind_preexisting = False
            if not breath:
                from app.combat.breathing import reset_breathing
                if not any(source.prevents_breathing for source in state.grapple_sources):
                    reset_breathing(state)
    except Exception:
        logger.exception("Failed to synchronize attachment-owned controls.")
        raise


def attachment_attack_target(existing: tuple[Attachment, ...], source_id: str) -> str | None:
    matches = {row.target_id for row in existing
               if row.source_id == source_id and row.source_target_lock}
    if len(matches) > 1:
        raise ValueError("Attachment source has conflicting locked targets.")
    return next(iter(matches), None)


def attachment_attack_advantage(existing: tuple[Attachment, ...], source_id: str,
                                target_id: str) -> int:
    return int(any(row.source_id == source_id and row.target_id == target_id
                   and row.source_advantage_against_target for row in existing))


def move_attached_sources_with_target(setup, target_id: str) -> None:
    members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
    target = members.get(target_id)
    if target is None:
        return
    for row in setup.attachments:
        if row.target_id == target_id and row.moves_with_target and row.source_id in members:
            members[row.source_id].position_ft = target.position_ft
