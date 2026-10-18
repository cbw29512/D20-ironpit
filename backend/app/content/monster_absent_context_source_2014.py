"""Fail-closed source proofs for 2014 abilities with absent combat contexts.

Only exact, immutable SRD clauses qualify. Printed names locate source
text, never select a runtime combat resolver. Standard arena combat has no
equipment corrosion, mounted riders, or Ethereal travel.
"""
from __future__ import annotations

from html import unescape
import logging
import re

logger = logging.getLogger(__name__)

_INERT_TRAIT_TEXTS = frozenset({
    "the rust monster can pinpoint, by scent, the location of ferrous metal within 30 feet of it.",
    "any nonmagical weapon made of metal that hits the rust monster corrodes. after dealing damage, the weapon takes a permanent and cumulative −1 penalty to damage rolls. if its penalty drops to −5, the weapon is destroyed. nonmagical ammunition made of metal that hits the rust monster is destroyed after dealing damage.",
    "the nightmare can grant resistance to fire damage to anyone riding it.",
})
_INERT_ACTION_TEXTS = frozenset({
    "the rust monster corrodes a nonmagical ferrous metal object it can see within 5 feet of it. if the object isn't being worn or carried, the touch destroys a 1-foot cube of it. if the object is being worn or carried by a creature, the creature can make a dc 11 dexterity saving throw to avoid the rust monster's touch. if the object touched is either metal armor or a metal shield being worn or carried, it takes a permanent and cumulative −1 penalty to the ac it offers. armor reduced to an ac of 10 or a shield that drops to a +0 bonus is destroyed. if the object touched is a held metal weapon, it rusts as described in the rust metal trait.",
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
