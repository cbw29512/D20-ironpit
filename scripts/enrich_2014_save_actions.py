from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from import_2014_recharge import parse_action_recharges
from import_2014_save_actions import parse_save_actions

logger = logging.getLogger(__name__)


def enrich(source_path: Path, catalog_path: Path) -> None:
    source_rows = json.loads(source_path.read_text(encoding="utf-8"))
    catalog_rows = json.loads(catalog_path.read_text(encoding="utf-8"))
    source_by_name = {row["name"]: row for row in source_rows}
    if len(source_by_name) != len(source_rows):
        raise ValueError("2014 source contains duplicate monster names.")
    for row in catalog_rows:
        source = source_by_name.get(row["name"])
        if source is None:
            raise ValueError(f"Missing pinned source row for {row['name']!r}.")
        actions = source.get("Actions", "")
        recharges = parse_action_recharges(actions)
        row["saving_throw_actions"] = parse_save_actions(actions, recharges)
    catalog_path.write_text(
        json.dumps(catalog_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Add typed 2014 save/AoE actions to a normalized catalog.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        enrich(args.source, args.catalog)
        print(f"enriched 2014 save actions in {args.catalog}")
        return 0
    except Exception as exc:
        logger.exception("2014 save-action enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
