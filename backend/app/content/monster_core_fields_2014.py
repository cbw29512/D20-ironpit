"""Source-owned combat values across the complete 2014 monster catalog.

This module exposes printed values; the one universal combat engine resolves them.
Unsupported actions remain blocked for admission rather than being discarded.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MonsterAttackFields2014:
    source_id: str
    name: str
    kind: str
    attack_bonus: int
    damage_dice_count: int
    damage_dice_size: int
    damage_bonus: int
    damage_type: str | None
    source_complete: bool


@dataclass(frozen=True, slots=True)
class MonsterCoreFields2014:
    source_id: str
    name: str
    armor_class: int
    max_hp: int
    dexterity_score: int
    initiative_bonus: int
    attacks: tuple[MonsterAttackFields2014, ...]
    blockers: tuple[str, ...]

    @property
    def runnable(self) -> bool:
        return not self.blockers


@lru_cache(maxsize=1)
def all_monster_core_fields_2014() -> tuple[MonsterCoreFields2014, ...]:
    """Read all 327 printed cards, independent of complete-action certification."""
    try:
        cards = load_monster_source_2014()
        rows: list[MonsterCoreFields2014] = []
        for card in cards:
            dexterity = card.abilities["dexterity"]
            rows.append(MonsterCoreFields2014(
                source_id=card.id,
                name=card.name,
                armor_class=card.armor_class,
                max_hp=card.max_hp,
                dexterity_score=dexterity,
                initiative_bonus=(dexterity - 10) // 2,
                attacks=tuple(
                    MonsterAttackFields2014(
                        source_id=attack.id,
                        name=attack.name,
                        kind=attack.kind,
                        attack_bonus=attack.attack_bonus,
                        damage_dice_count=attack.damage.dice_count,
                        damage_dice_size=attack.damage.dice_size,
                        damage_bonus=attack.damage.bonus,
                        damage_type=attack.damage.type,
                        source_complete=attack.source_complete,
                    )
                    for attack in card.attacks
                ),
                blockers=basic_blockers_2014(card),
            ))
        if len(rows) != 327 or len({row.source_id for row in rows}) != 327:
            raise ValueError("Complete 2014 catalog requires 327 unique monster cards.")
        return tuple(rows)
    except Exception:
        logger.exception("Failed to bind all 2014 monsters' core combat fields.")
        raise


def monster_core_fields_2014(source_id: str) -> MonsterCoreFields2014:
    """Look up immutable card data; combat still uses canonical state/resolvers."""
    try:
        return next(row for row in all_monster_core_fields_2014() if row.source_id == source_id)
    except StopIteration as exc:
        logger.error("Unknown 2014 monster source ID: %s", source_id)
        raise KeyError(f"Unknown 2014 monster source ID: {source_id}") from exc
    except Exception:
        logger.exception("2014 monster field lookup failed: %s", source_id)
        raise
