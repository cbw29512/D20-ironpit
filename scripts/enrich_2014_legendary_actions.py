from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from import_2014_legendary_actions import parse_legendary_actions

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 legendary actions from pinned source text.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        source = json.loads(args.source.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        by_name = {row["name"]: row for row in catalog}
        parsed_options = 0
        for raw in source:
            row = by_name.get(raw["name"])
            if row is None:
                continue
            uses, options, unsupported = parse_legendary_actions(
                raw.get("Legendary Actions"), row.get("attacks", [])
            )
            row["legendary_action_uses"] = uses
            row["legendary_actions"] = options
            row["unsupported_legendary_action_names"] = unsupported
            parsed_options += len(options)
        args.catalog.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"enriched {parsed_options} legendary action options")
        return 0
    except Exception as exc:
        logger.exception("2014 legendary action enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
