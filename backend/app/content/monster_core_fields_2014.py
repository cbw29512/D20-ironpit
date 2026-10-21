"""Immutable core combat fields for every 2014 monster, including blocked cards.

This is a source-data bridge, not a second combat engine or a bypass around
full combat admission. Runtime resolution still uses the universal engine.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MonsterCoreFields2014:
    source_id: str
    name: str
    armor_class: int
    max_hp: int
    blockers: tuple[str, ...]

    @property
    def runnable(self) -> bool:
        return not self.blockers


@lru_cache(maxsize=1)
def all_monster_core_fields_2014() -> tuple[MonsterCoreFields2014, ...]:
    """Keep printed AC/HP available for all 327, including non-runnable cards."""
    try:
        cards = load_monster_source_2014()
        fields = tuple(
            MonsterCoreFields2014(
                source_id=card.id,
                name=card.name,
                armor_class=card.armor_class,
                max_hp=card.max_hp,
                blockers=basic_blockers_2014(card),
            )
            for card in cards
        )
        if len(fields) != 327 or len({row.source_id for row in fields}) != 327:
            raise ValueError("The complete 2014 core-stat bridge requires 327 unique cards.")
        return fields
    except Exception:
        logger.exception("Could not build complete 2014 monster core-stat bindings.")
        raise


def monster_core_fields_2014(source_id: str) -> MonsterCoreFields2014:
    """Read source-owned statistics without pretending unsupported actions work."""
    try:
        return next(row for row in all_monster_core_fields_2014() if row.source_id == source_id)
    except StopIteration as exc:
        logger.error("Unknown 2014 monster source id: %s", source_id)
        raise KeyError(f"Unknown 2014 monster source id: {source_id}") from exc
    except Exception:
        logger.exception("Failed 2014 core-stat lookup for %s", source_id)
        raise
