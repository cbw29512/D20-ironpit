"""Source-neutral guard: an active attached owner may be forbidden to attack."""
from __future__ import annotations

import logging

from app.domain.encounters import EncounterSetup

logger = logging.getLogger(__name__)


def source_attacks_blocked(setup: EncounterSetup | None, source_id: str) -> bool:
    """Only source-specified blocks_source_attacks restricts attack eligibility."""
    try:
        if setup is None:
            return False
        return any(
            row.source_id == source_id and row.blocks_source_attacks
            for row in setup.attachments
        )
    except Exception:
        logger.exception("Attachment attack eligibility failed for %s.", source_id)
        raise
