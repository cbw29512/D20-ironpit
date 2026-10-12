"""Source-backed, duration-free combat conditions from 2014 printed traits.

The source text is immutable; the shared condition engine owns all mechanics.
No creature IDs are consulted. Unsupported innate traits remain blocked.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.action_types import ConditionName

logger = logging.getLogger(__name__)

# Only the exact unconditional declaration is a starting condition.
# An action, saving throw, temporary spell or "can become invisible" does not match.
_INVISIBLE_DECLARATION = re.compile(
    r"<strong>Invisibility\.</strong>\s*[^<.]{1,100}?\bis invisible\.",
    re.IGNORECASE,
)


def innate_condition_ids_2014(monster: SourceMonster2014) -> list[ConditionName]:
    """Bind unconditional printed status to a shared, fight-local condition."""
    try:
        if "Invisibility" not in monster.trait_names:
            return []
        if not _INVISIBLE_DECLARATION.search(monster.source_traits or ""):
            return []
        return ["invisible"]
    except Exception:
        logger.exception("2014 innate-condition source binding failed for %s.", monster.id)
        raise
