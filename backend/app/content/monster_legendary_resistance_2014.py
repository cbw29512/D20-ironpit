from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.combatants import ResourceDefinition
from app.domain.save_success_overrides import FailedSaveSuccessOverride

logger = logging.getLogger(__name__)
_LR = re.compile(r"^Legendary Resistance \((\d+)/Day\)$")
RESOURCE_ID = "legendary-resistance"


def legendary_resistance_uses_2014(monster: SourceMonster2014) -> int:
    """Parse printed Legendary Resistance uses from the pinned trait name."""
    try:
        for name in monster.trait_names:
            match = _LR.fullmatch(name)
            if match is None:
                continue
            uses = int(match.group(1))
            if not 1 <= uses <= 10:
                raise ValueError(f"{monster.id} has invalid Legendary Resistance uses {uses}.")
            return uses
        return 0
    except Exception:
        logger.exception("Failed to parse Legendary Resistance for %s.", monster.id)
        raise


def legendary_resistance_trait_name_2014(monster: SourceMonster2014) -> str | None:
    try:
        uses = legendary_resistance_uses_2014(monster)
        return f"Legendary Resistance ({uses}/Day)" if uses else None
    except Exception:
        logger.exception("Failed to name Legendary Resistance for %s.", monster.id)
        raise


def legendary_resistance_resource_2014(monster: SourceMonster2014) -> ResourceDefinition | None:
    try:
        uses = legendary_resistance_uses_2014(monster)
        if uses <= 0:
            return None
        return ResourceDefinition(id=RESOURCE_ID, name="Legendary Resistance", max_uses=uses)
    except Exception:
        logger.exception("Failed to build Legendary Resistance resource for %s.", monster.id)
        raise


def legendary_resistance_override_2014(monster: SourceMonster2014) -> FailedSaveSuccessOverride | None:
    try:
        if legendary_resistance_uses_2014(monster) <= 0:
            return None
        return FailedSaveSuccessOverride(
            source_id=RESOURCE_ID,
            source_name="Legendary Resistance",
            resource_id=RESOURCE_ID,
        )
    except Exception:
        logger.exception("Failed to bind Legendary Resistance for %s.", monster.id)
        raise
