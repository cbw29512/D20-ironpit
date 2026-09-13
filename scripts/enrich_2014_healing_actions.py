from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_healing_actions import parse_limited_healing_action

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 limited-use healing actions from pinned source text.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        source = json.loads(args.source.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        by_name = {row["name"]: row for row in catalog}
        parsed_count = 0
        for raw in source:
            row = by_name.get(raw["name"])
            if row is None: continue
            existing = {action["id"] for action in row.get("healing_actions", [])}
            for paragraph in re.findall(r"<p>(.*?)</p>", raw.get("Actions", ""), re.I | re.S):
                parsed = parse_limited_healing_action(paragraph)
                if parsed is None: continue
                action, uses = parsed
                if action["id"] in existing: continue
                row.setdefault("healing_actions", []).append(action)
                row.setdefault("limited_action_uses", {})[action["resource_id"]] = uses
                existing.add(action["id"]); parsed_count += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed_count} limited healing actions")
        return 0
    except Exception as exc:
        logger.exception("2014 healing action enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
