"""Print 327-card damage defense binding coverage; no combat simulation.

Usage: PYTHONPATH=backend python scripts/report_monster_defenses_2014.py
"""
from __future__ import annotations

import json
import logging
from collections import Counter

from app.content.monster_conditional_damage_defenses_2014 import (
    remaining_unsupported_defense_text_2014,
    template_defense_fields_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def report() -> dict[str, object]:
    """Classify printed defenses independently of other monster blockers."""
    monsters = load_monster_source_2014()
    counts: Counter[str] = Counter()
    unresolved: list[dict[str, object]] = []
    for monster in monsters:
        # Reuse precisely the defense compiler used by admitted combatants.
        fields = template_defense_fields_2014(monster)
        for field in (
            "damage_resistances", "damage_vulnerabilities",
            "damage_immunities", "damage_absorptions",
            "conditional_damage_defenses",
        ):
            if fields[field]:
                counts[field] += 1
        missing = remaining_unsupported_defense_text_2014(monster)
        if missing:
            unresolved.append({"monster_id": monster.id, "clauses": missing})
    if len(monsters) != 327:
        raise ValueError(f"Expected 327 2014 monsters, found {len(monsters)}")
    return {
        "source_monsters": len(monsters),
        "cards_with_declared_defenses": dict(sorted(counts.items())),
        "unresolved_damage_defense_cards": len(unresolved),
        "unresolved": unresolved,
    }


if __name__ == "__main__":
    try:
        print(json.dumps(report(), indent=2, sort_keys=True))
    except Exception:
        logger.exception("Unable to report complete 2014 damage-defense coverage")
        raise
