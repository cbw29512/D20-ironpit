"""Source-neutral guard: an active attached owner may be forbidden to attack."""
from __future__ import annotations

import logging

from app.domain.encounters import EncounterSetup

logger = logging.getLogger(__name__)


def source_attacks_blocked(setup: EncounterSetup | None, source_id: str,
                           target_id: str | None = None) -> bool:
    """Only source-specified blocks_source_attacks restricts attack eligibility."""
    try:
        if setup is None:
            return False
        if any(
            row.source_id == source_id and row.blocks_source_attacks
            for row in setup.attachments
        ):
            return True
        locked = {row.target_id for row in setup.attachments
                  if row.source_id == source_id and row.source_target_lock}
        return bool(locked and target_id not in locked)
    except Exception:
        logger.exception("Attachment attack eligibility failed for %s.", source_id)
        raise
