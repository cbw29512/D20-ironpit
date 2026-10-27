"""Roster-wide source-to-browser trait retention audit.

State schema: each row records monster id, source traits, compiled traits,
browser traits, missing names and arena-neutral names. No fight state changes.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_arena_neutral_traits_2014 import (
    ARENA_NEUTRAL_TRAITS_2014,
    verified_arena_inert_trait_2014,
)
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row

LOGGER = logging.getLogger(__name__)


def audit_traits() -> list[dict]:
    """Compare all 327 sources; report blocked monsters without claiming cards exist."""
    try:
        source = load_monster_source_2014()
        compiled = {t.id: t for t in build_basic_2014_monsters()}
        rows = []
        for monster in source:
            ident = f"2014-{monster.id}"
            template = compiled.get(ident)
            expected = set(monster.trait_names)
            actual = set(template.source_trait_names) if template else set()
            browser = set(template_row(template).get("source_trait_names", [])) if template else set()
            neutral = sorted(name for name in expected if name in ARENA_NEUTRAL_TRAITS_2014
                             or verified_arena_inert_trait_2014(monster, name))
            rows.append({
                "monster_id": monster.id,
                "name": monster.name,
                "compiled": template is not None,
                "source_trait_count": len(expected),
                "arena_neutral_traits": neutral,
                "missing_definition": sorted(expected - actual) if template else [],
                "missing_browser": sorted(expected - browser) if template else [],
                "presentation_verified": False,
            })
        return rows
    except Exception:
        LOGGER.exception("2014 monster-card trait audit failed.")
        raise


def main() -> None:
    try:
        rows = audit_traits()
        output = Path("docs/generated/MONSTER_CARD_TRAIT_AUDIT_2014.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        compiled = sum(row["compiled"] for row in rows)
        missing = sum(len(row["missing_definition"]) + len(row["missing_browser"]) for row in rows)
        print(f"Audited {len(rows)} 2014 source monsters; compiled {compiled}; retention gaps {missing}.")
        print("Browser presentation remains UNVERIFIED: names are not proof of greyed-out cards.")
        if len(rows) != 327 or missing:
            raise SystemExit("Source/serialized monster trait completeness audit failed.")
    except Exception:
        LOGGER.exception("Could not export 2014 monster-card audit.")
        raise


if __name__ == "__main__":
    main()
