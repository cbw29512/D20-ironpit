"""Source-neutral owner/host link lifecycle for future control resolution.

No source attack is installed here. Callers must establish target eligibility,
spend the Action and resolve the save before invoking this link operation.
"""
from __future__ import annotations

import logging

from app.domain.body_control import BodyControlLink
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def start_body_control_link(
    owner_id: str, owner: CombatantState, host_id: str, host: CombatantState,
    *, source_action_id: str, source_name: str, round_number: int,
    failed_save: bool,
) -> bool:
    """Record one confirmed body-control relationship without source mutation."""
    try:
        if not failed_save:
            return False
        # Never overwrite another live owner, or silently create a second host.
        if owner_id == host_id or host.controlled_by is not None:
            return False
        if owner.controlling_target_ids:
            return False
        if (not owner.is_alive or owner.is_dead or owner.current_hp <= 0
                or not host.is_alive or host.is_dead or host.current_hp <= 0):
            return False
        link = BodyControlLink(
            source_id=owner_id, source_action_id=source_action_id,
            source_name=source_name, host_id=host_id,
            started_round=round_number,
        )
        host.controlled_by = link
        owner.controlling_target_ids.append(host_id)
        return True
    except Exception:
        logger.exception("Body-control link start failed: %s -> %s", owner_id, host_id)
        raise


def end_body_control_link(
    owner_id: str, owner: CombatantState, host_id: str, host: CombatantState,
) -> bool:
    """End only the matching owner/host link; preserve independent conditions."""
    try:
        link = host.controlled_by
        if link is None or link.source_id != owner_id or link.host_id != host_id:
            return False
        if host_id not in owner.controlling_target_ids:
            raise ValueError("Body-control link has no matching source ownership.")
        owner.controlling_target_ids.remove(host_id)
        host.controlled_by = None
        return True
    except Exception:
        logger.exception("Body-control link release failed: %s -> %s", owner_id, host_id)
        raise
