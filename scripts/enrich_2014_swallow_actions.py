from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_swallow_actions import parse_swallow_action

logger = logging.getLogger(__name__)


def _parse_swallow_from_actions(actions: str) -> dict | None:
    paragraphs = re.findall(r"<p>(.*?)</p>", actions or "", re.I | re.S)
    for index, paragraph in enumerate(paragraphs):
        parsed = parse_swallow_action(paragraph)
        if parsed is not None:
            return parsed
        if index + 1 < len(paragraphs):
            parsed = parse_swallow_action(f"{paragraph} {paragraphs[index + 1]}")
            if parsed is not None:
                return parsed
    return None


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
            if row is None:
                continue
            parsed = _parse_swallow_from_actions(raw.get("Actions", ""))
            if parsed is None:
                continue
            row["swallow_actions"] = [parsed]
            parsed_count += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed_count} swallow actions")
        return 0
    except Exception as exc:
        logger.exception("2014 Swallow enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
