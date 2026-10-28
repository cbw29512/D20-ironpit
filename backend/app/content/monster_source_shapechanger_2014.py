"""Source-verified 2014 Shapechanger trait foundation.

Source-neutral classifier and binder for the common Shapechanger trait.
No name dispatch. Reuses existing transformation primitives where present.
"""
from __future__ import annotations

import logging
import re
from html import unescape

logger = logging.getLogger(__name__)

_REQUIRED_CLAUSES = (
    "can use its action to polymorph",
    "or back into its true form",
    "statistics, other than its size, are the same",
    "equipment it is wearing or carrying isn't transformed",
    "reverts to its true form if it dies",
)


def is_source_shapechanger_2014(source_traits: str) -> bool:
    """Return True only if the printed trait matches the verified Shapechanger pattern."""
    try:
        if not source_traits:
            return False
        text = " ".join(unescape(re.sub(r"<[^>]+>", " ", source_traits)).split()).casefold()
        return all(clause in text for clause in _REQUIRED_CLAUSES)
    except Exception:
        logger.exception("Shapechanger source verification failed")
        return False
