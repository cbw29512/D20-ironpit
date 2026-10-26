"""Semantic discovery for staged disease clauses in immutable 2014 cards."""
from __future__ import annotations

import re

from app.content.monster_source_2014 import SourceMonster2014

_TAGS = (
    "disease has no effect for 1 minute",
    "after 1 minute",
    "disease can be removed only by",
    "disease-curing spell of 6th level or higher",
)


def _plain(text: str | None) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip().casefold()


def semantic_staged_disease_2014(card: SourceMonster2014) -> bool:
    """Match the printed staged lifecycle without consulting monster or action names."""
    text = _plain(card.source_actions)
    return all(token in text for token in _TAGS)


def staged_disease_candidates_2014(
    cards: tuple[SourceMonster2014, ...],
) -> tuple[SourceMonster2014, ...]:
    return tuple(card for card in cards if semantic_staged_disease_2014(card))
