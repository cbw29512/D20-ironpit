from __future__ import annotations

import logging
import re

from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)

_SOURCE_GRAPPLE_ADVANTAGE = re.compile(
    r"^\s*\(\s*with\s+Advantage\s+if\s+the\s+target\s+is\s+Grappled\s+by\s+the\s+[^)]+\)\s*$",
    re.IGNORECASE,
)


def parse_attack_header_advantage(note: str | None) -> list[ConditionalAttackAdvantage]:
    """Compile supported source-header Advantage clauses into universal runtime data."""
    try:
        if not note:
            return []
        if _SOURCE_GRAPPLE_ADVANTAGE.fullmatch(note):
            return [ConditionalAttackAdvantage(trigger="target_grappled_by_source")]
        raise ValueError(f"Unsupported attack-header Advantage clause: {note!r}.")
    except Exception:
        logger.exception("Failed to parse source attack-header Advantage clause.")
        raise


__all__ = ["parse_attack_header_advantage"]
