"""Fail-closed source proofs for 2014 abilities with absent combat contexts.

Only exact, immutable SRD clauses qualify. Printed names locate source
text, never select a runtime combat resolver. Standard arena combat has no
mounted riders or Ethereal travel.
"""
from __future__ import annotations

from html import unescape
import logging
import re

logger = logging.getLogger(__name__)

_INERT_TRAIT_TEXTS = frozenset({
    "the nightmare can grant resistance to fire damage to anyone riding it.",
})
_INERT_ACTION_TEXTS = frozenset({
    "the nightmare and up to three willing creatures within 5 feet of it magically enter the ethereal plane from the material plane, or vice versa.",
})


def _normalized(value: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]*>", "", value)).split()).casefold()


def _complete_source_sections(source: str | None) -> dict[str, str]:
    """Retain unheaded continuation paragraphs, which the basic parser omits."""
    try:
        sections: dict[str, str] = {}
        current: str | None = None
        for paragraph in re.findall(r"<p>(.*?)</p>", source or "", re.S):
            heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.S)
            if heading:
                current = _normalized(heading.group(1)).rstrip(".")
                sections[current] = _normalized(paragraph[heading.end():])
            elif current is not None:
                sections[current] += " " + _normalized(paragraph)
        return sections
    except Exception:
        logger.exception("Failed to parse pinned 2014 source paragraphs")
        raise


def verified_absent_context_trait_2014(monster, name: str) -> bool:
    try:
        return name in monster.trait_names and _complete_source_sections(monster.source_traits).get(name.casefold()) in _INERT_TRAIT_TEXTS
    except Exception:
        logger.exception("Arena-neutral trait proof failed: %s / %s", monster.id, name)
        raise


def verified_absent_context_action_2014(monster, name: str) -> bool:
    try:
        return name in monster.action_names and _complete_source_sections(monster.source_actions).get(name.casefold()) in _INERT_ACTION_TEXTS
    except Exception:
        logger.exception("Arena-neutral action proof failed: %s / %s", monster.id, name)
        raise
