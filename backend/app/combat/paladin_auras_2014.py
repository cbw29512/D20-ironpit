from __future__ import annotations

import logging

from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.domain.encounters import EncounterSetup

logger = logging.getLogger(__name__)


def sync_paladin_auras_2014(setup: EncounterSetup) -> None:
    """Compatibility entrypoint; universal friendly aura sync owns all mechanics."""
    try:
        sync_friendly_save_auras(setup)
    except Exception:
        logger.exception("Failed to synchronize 2014 Paladin auras.")
        raise
