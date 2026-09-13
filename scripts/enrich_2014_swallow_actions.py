from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_swallow_actions import parse_swallow_action

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 Swallow actions from pinned source text.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        source = json.loads(args.source.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        by_name = {row["name"]: row for row in catalog}; parsed_count = 0
        for raw in source:
            row = by_name.get(raw["name"])
            if row is None: continue
            for paragraph in re.findall(r"<p>(.*?)</p>", raw.get("Actions", ""), re.I | re.S):
                parsed = parse_swallow_action(paragraph)
                if parsed is None: continue
                row["swallow_actions"] = [parsed]; parsed_count += 1; break
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed_count} swallow actions")
        return 0
    except Exception as exc:
        logger.exception("2014 Swallow enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
