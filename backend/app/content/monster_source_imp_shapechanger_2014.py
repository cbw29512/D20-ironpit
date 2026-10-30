"""Source-verified 2014 Imp Shapechanger foundation.

Binds to existing universal replacement-form primitives. No name dispatch.
Source supplies form list, speed overrides, and lifecycle. Engine supplies form change behavior.
Does not admit the monster; remaining blockers stay.
"""
from __future__ import annotations

import logging
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

_REQUIRED_CLAUSES = (
    "polymorph into a beast form",
    "rat",
    "raven",
    "spider",
    "statistics are the same",
    "reverts to its true form",
)

def is_imp_shapechanger_source(monster: SourceMonster2014) -> bool:
    try:
        if monster.id != "imp":
            return False
        source = monster.source_traits or ""
        section = " ".join(source.split()).casefold()
        return all(clause in section for clause in _REQUIRED_CLAUSES)
    except Exception:
        logger.exception("Imp Shapechanger source proof failed")
        return False
