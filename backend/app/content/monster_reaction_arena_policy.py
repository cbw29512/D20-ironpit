from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_SPLIT_EXTRA_COMBATANTS = re.compile(
    r"\bResponse:\s+The [^.]+ splits into two new [^.]+\.\s+"
    r"Each new [^.]+ acts on its Initiative\.\s+"
    r"The original [^.]+ Hit Points are divided evenly between the new [^.]+",
    re.IGNORECASE,
)


def arena_unavailable_reaction(name: str, source_reactions: object) -> bool:
    """Classify printed reactions whose only outcome is forbidden extra-combatant creation."""
    try:
        text = str(source_reactions or "").strip()
        if not text:
            return False
        if name.strip().lower() != "split":
            return False
        return _SPLIT_EXTRA_COMBATANTS.search(text) is not None
    except Exception as exc:
        logger.exception("Failed to classify arena-unavailable reaction %r.", name)
        raise RuntimeError("Arena-unavailable reaction policy could not be evaluated.") from exc


__all__ = ["arena_unavailable_reaction"]
