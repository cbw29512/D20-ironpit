"""Source-backed, duration-free combat conditions from printed 2014 traits.

Use the existing Invisible condition; never construct monster-specific combat
logic. Parsing must prove the *whole* unconditional printed source clause.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.action_types import ConditionName

logger = logging.getLogger(__name__)

# An action, spell, save, temporary buff or "can become invisible" is not
# an always-on Invisible trait. The printed source states the condition.
_ALWAYS_INVISIBLE_CLAUSE = re.compile(r"the [a-z][a-z-]* is invisible\\.", re.IGNORECASE)


def innate_condition_ids_2014(monster: SourceMonster2014) -> list[ConditionName]:
    """Bind an exact unconditional printed status to the shared condition."""
    try:
        if "Invisibility" not in monster.trait_names:
            return []
        printed = source_sections_2014(monster.source_traits).get("Invisibility", "")
        if not _ALWAYS_INVISIBLE_CLAUSE.fullmatch(printed.strip()):
            return []
        return ["invisible"]
    except Exception:
        logger.exception("2014 innate-condition source binding failed for %s.", monster.id)
        raise
