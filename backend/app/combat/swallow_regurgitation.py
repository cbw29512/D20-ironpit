"""Shared damage-threshold regurgitation for source-declared Swallow effects."""
from __future__ import annotations

import logging

from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.swallow_state import release_swallowed

logger = logging.getLogger(__name__)


def resolve_swallow_regurgitation(
    owner, swallowed_target, *, owner_id: str, target_id: str,
    damage_from_swallowed_on_turn: int, dice, round_number: int,
    owner_member=None, setup=None,
) -> tuple[bool, object | None]:
    """Consume a source-defined threshold and normal save; release on failure.

    Caller must aggregate only actual damage inflicted by this swallowed target
    on a single turn; unrelated damage must not count toward the threshold.
    """
    try:
        record = swallowed_target.swallowed
        if record is None or record.source_id != owner_id:
            return False, None
        threshold = record.regurgitation_damage_threshold
        if threshold is None or damage_from_swallowed_on_turn < threshold:
            return False, None
        if record.regurgitation_save_ability is None or record.regurgitation_save_dc is None:
            raise ValueError("Regurgitation threshold requires a printed saving throw.")
        roll, success = resolve_saving_throw(
            owner, record.regurgitation_save_ability,
            record.regurgitation_save_dc, dice,
            round_number=round_number,
            encounter_roller=owner_member, setup=setup,
        )
        if success:
            return False, roll
        released = release_swallowed(
            owner, target_id, swallowed_target, owner_id=owner_id,
            exiting_prone=True,
        )
        return released, roll
    except Exception:
        logger.exception(
            "Failed source-neutral regurgitation check for owner=%s target=%s",
            owner_id, target_id,
        )
        raise
