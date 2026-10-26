"""Semantic 2014 roster scan for passive hostile fear auras."""
from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)


def semantic_fear_aura_candidate_2014(monster: SourceMonster2014) -> bool:
    """Detect printed behavior or damaged semantic tokens without identity keys."""
    try:
        text = html.unescape(
            re.sub(r"<[^>]+>", " ", str(monster.source_traits or ""))
        )
        normalized = " ".join(text.casefold().split())
        full_markers = (
            "starts its turn",
            "saving throw",
            "incapacitated",
            "frightened",
            "immune",
        )
        return (
            all(marker in normalized for marker in full_markers)
            or "incapacitatedfrightened" in normalized
        )
    except Exception:
        logger.exception("Failed Fear Aura semantic scan for %s.", monster.id)
        raise
