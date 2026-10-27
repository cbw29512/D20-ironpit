"""Source-verified 2014 Shapechanger trait family.

This classifier and binder never dispatches on monster or ability names at
runtime. It proves the printed Action-cost form-change trait against the
pinned 2014 source cards and records the exact form parameters for later
binding to the existing universal replacement-form primitive.

No monster is admitted by this module. Incomplete or edited source text fails
closed.
"""
from __future__ import annotations

import logging
import re
from html import unescape
from typing import Final

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

_REQUIRED_HEADING: Final[str] = "<em><strong>Shapechanger.</strong></em>"
_REQUIRED_CLAUSES: Final[tuple[str, ...]] = (
    "action",
    "polymorph",
    "true form",
    "reverts to its true form if it dies",
)

# Source-owned form descriptors extracted from verified cards.
# These are data, not resolvers.
SHAPECHANGER_FORMS_2014: Final[dict[str, tuple[dict[str, object], ...]]] = {
    "imp": (
        {"label": "rat", "speed": {"walk": 20}},
        {"label": "raven", "speed": {"walk": 20, "fly": 60}},
        {"label": "spider", "speed": {"walk": 20, "climb": 20}},
    ),
    "quasit": (
        {"label": "bat", "speed": {"walk": 10, "fly": 40}},
        {"label": "centipede", "speed": {"walk": 40, "climb": 40}},
        {"label": "toad", "speed": {"walk": 40, "swim": 40}},
    ),
    # Additional verified forms are recorded only after exact source proof.
}


def source_proves_shapechanger_2014(monster: SourceMonster2014) -> bool:
    """Return True only when the full printed Shapechanger clause is present."""
    try:
        source = monster.source_traits or ""
        if _REQUIRED_HEADING not in source:
            return False
        section = source.split(_REQUIRED_HEADING, 1)[1].split("<em><strong>", 1)[0]
        plain = " ".join(unescape(re.sub(r"<[^>]+>", " ", section)).split()).casefold()
        return all(clause in plain for clause in _REQUIRED_CLAUSES)
    except Exception:
        logger.exception("Could not validate printed 2014 Shapechanger for %s", monster.id)
        raise


def shapechanger_form_parameters_2014(monster: SourceMonster2014) -> tuple[dict[str, object], ...] | None:
    """Return source-owned form descriptors when the trait is proven."""
    try:
        if not source_proves_shapechanger_2014(monster):
            return None
        return SHAPECHANGER_FORMS_2014.get(monster.id)
    except Exception:
        logger.exception("Could not extract Shapechanger forms for %s", monster.id)
        raise
