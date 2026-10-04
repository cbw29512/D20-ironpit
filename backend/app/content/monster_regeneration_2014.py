from __future__ import annotations

import logging

from app.domain.regeneration import RegenerationTrait
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)


def regeneration_trait_2014(monster: SourceMonster2014) -> RegenerationTrait | None:
    """Compile a pinned 2014 Regeneration object into the shared trait."""
    try:
        raw = monster.regeneration
        if raw is None:
            return None
        if not isinstance(raw, dict):
            raise ValueError(f"{monster.id} Regeneration must be a declarative object.")
        return RegenerationTrait.model_validate(raw)
    except Exception:
        logger.exception("Failed to compile 2014 Regeneration for %s.", monster.id)
        raise


def supports_regeneration_2014(monster: SourceMonster2014) -> bool:
    """Return whether printed Regeneration can bind to the shared primitive."""
    try:
        return regeneration_trait_2014(monster) is not None
    except Exception:
        logger.exception("Failed to classify 2014 Regeneration for %s.", monster.id)
        raise
