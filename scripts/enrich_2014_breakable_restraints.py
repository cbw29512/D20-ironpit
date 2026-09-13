from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_breakable_restraints import parse_breakable_restraint_attack

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 attack-roll restraints from pinned source text.")
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
            recharges = row.get("action_recharges", {})
            existing = {attack["id"] for attack in row.get("attacks", [])}
            for paragraph in re.findall(r"<p>(.*?)</p>", raw.get("Actions", ""), re.I | re.S):
                parsed = parse_breakable_restraint_attack(paragraph, recharges)
                if parsed is None or parsed["id"] in existing:
                    continue
                row.setdefault("attacks", []).append(parsed)
                existing.add(parsed["id"])
                parsed_count += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed_count} breakable restraint attacks")
        return 0
    except Exception as exc:
        logger.exception("2014 breakable restraint enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
