#!/usr/bin/env python3
"""Audit every pinned 2014 Recharge action against universal engine bindings."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_save_capabilities_2014 import (
    save_capabilities_2014,
    supports_recharge_rules_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def recharge_rows() -> list[dict[str, object]]:
    try:
        rows: list[dict[str, object]] = []
        for monster in load_monster_source_2014():
            if not monster.action_recharges:
                continue
            sections = source_sections_2014(
                monster.source_actions, include_continuations=True,
            )
            capabilities = save_capabilities_2014(monster)
            capability_ids = {item.id for item in capabilities}
            resource_ids = {
                item.resource_id for item in capabilities if item.resource_id is not None
            }
            actions = []
            for action_id, minimum in sorted(monster.action_recharges.items()):
                label = action_id.replace("-", " ").casefold()
                headings = [
                    heading for heading in sections
                    if heading.split(" (Recharge", 1)[0].strip().casefold() == label
                ]
                actions.append({
                    "resource_id": action_id,
                    "minimum_roll": minimum,
                    "source_headings": headings,
                    "source_text": [sections[heading] for heading in headings],
                    "bound_as_save_action": action_id in capability_ids,
                    "bound_as_save_resource": action_id in resource_ids,
                })
            rows.append({
                "monster_id": monster.id,
                "monster_name": monster.name,
                "recharge_supported": supports_recharge_rules_2014(monster),
                "actions": actions,
            })
        return rows
    except Exception:
        logger.exception("2014 Recharge source audit failed.")
        raise


def main() -> int:
    try:
        rows = recharge_rows()
        print("2014_RECHARGE_AUDIT_SUMMARY\t" + json.dumps({
            "cards": len(rows),
            "supported": sum(bool(row["recharge_supported"]) for row in rows),
            "blocked": sum(not bool(row["recharge_supported"]) for row in rows),
        }, sort_keys=True))
        for row in rows:
            print("2014_RECHARGE_AUDIT\t" + json.dumps(row, sort_keys=True))
        return 0
    except Exception:
        logger.exception("2014 Recharge report failed.")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
