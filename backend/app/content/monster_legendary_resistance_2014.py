from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.combatants import ResourceDefinition
from app.domain.save_success_overrides import FailedSaveSuccessOverride

logger = logging.getLogger(__name__)
_LR = re.compile(r"^Legendary Resistance \((\d+)/Day(?:, or \d+/Day in Lair)?\)$", re.I)
RESOURCE_ID = "legendary-resistance"


def is_legendary_resistance_trait(name: str) -> bool:
    return _LR.fullmatch(str(name or "").strip()) is not None


def legendary_resistance_uses_from_names(names: list[str], *, owner: str) -> int:
    """Parse printed Legendary Resistance uses. Lair alternates use the non-lair count."""
    try:
        for name in names:
            match = _LR.fullmatch(str(name or "").strip())
            if match is None:
                continue
            uses = int(match.group(1))
            if not 1 <= uses <= 10:
                raise ValueError(f"{owner} has invalid Legendary Resistance uses {uses}.")
            return uses
        return 0
    except Exception:
        logger.exception("Failed to parse Legendary Resistance for %s.", owner)
        raise


def legendary_resistance_uses_2014(monster: SourceMonster2014) -> int:
    """Parse printed Legendary Resistance uses from the pinned trait name."""
    return legendary_resistance_uses_from_names(monster.trait_names, owner=monster.id)


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
        printed = legendary_resistance_trait_name_2014(monster) or "Legendary Resistance"
        return ResourceDefinition(id=RESOURCE_ID, name=printed, max_uses=uses)
    except Exception:
        logger.exception("Failed to build Legendary Resistance resource for %s.", monster.id)
        raise


def legendary_resistance_override_2014(monster: SourceMonster2014) -> FailedSaveSuccessOverride | None:
    try:
        if legendary_resistance_uses_2014(monster) <= 0:
            return None
        printed = legendary_resistance_trait_name_2014(monster) or "Legendary Resistance"
        return FailedSaveSuccessOverride(
            source_id=RESOURCE_ID,
            source_name=printed,
            resource_id=RESOURCE_ID,
        )
    except Exception:
        logger.exception("Failed to bind Legendary Resistance for %s.", monster.id)
        raise
