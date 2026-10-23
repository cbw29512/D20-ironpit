from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)


def non_offensive_dodge_inventory_2014(
    monsters: tuple[SourceMonster2014, ...] | list[SourceMonster2014],
) -> dict[str, object]:
    """Inventory every immutable 2014 card without a printed attack."""
    try:
        applicable = [monster for monster in monsters if not monster.attacks]
        wired = [
            monster for monster in applicable
            if not basic_blockers_2014(monster)
        ]
        remaining = [
            {
                "monster_id": monster.id,
                "monster_name": monster.name,
                "blockers": list(basic_blockers_2014(monster)),
            }
            for monster in applicable
            if basic_blockers_2014(monster)
        ]
        return {
            "schema_version": 1,
            "mechanic": "non-offensive-dodge-fallback",
            "source_card_count": len(monsters),
            "applicable_card_count": len(applicable),
            "wired_card_count": len(wired),
            "remaining_card_count": len(remaining),
            "wired": [
                {"monster_id": monster.id, "monster_name": monster.name}
                for monster in wired
            ],
            "exceptions": remaining,
        }
    except Exception:
        logger.exception("Failed to inventory 2014 non-offensive Dodge cards.")
        raise
