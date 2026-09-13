from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_death_triggers import parse_death_trigger

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 on-death save triggers from pinned source text.")
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
            if row is None:
                continue
            existing = {action["id"] for action in row.get("death_trigger_actions", [])}
            for paragraph in re.findall(r"<p>(.*?)</p>", raw.get("Traits", ""), re.I | re.S):
                action = parse_death_trigger(paragraph)
                if action is None or action["id"] in existing:
                    continue
                row.setdefault("death_trigger_actions", []).append(action)
                existing.add(action["id"]); parsed_count += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed_count} death-trigger actions")
        return 0
    except Exception as exc:
        logger.exception("2014 death-trigger enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
