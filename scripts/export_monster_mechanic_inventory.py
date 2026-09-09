from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
OUTPUT = ROOT / "data" / "monster_mechanic_inventory_v1.json"
sys.path.insert(0, str(BACKEND))

from app.content.monster_blocker_inventory import (  # noqa: E402
    blocker_family_incidence,
    build_monster_blocker_inventory,
)


def _payload() -> dict[str, object]:
    _, ready_names, blockers_by_name = build_monster_blocker_inventory()
    incidence = blocker_family_incidence(blockers_by_name)
    unclassified = sorted(
        name
        for name, blockers in blockers_by_name.items()
        if "unclassified-source-audit-gap" in blockers
    )
    return {
        "schema_version": 1,
        "ruleset": "srd-5.2.1-2024",
        "summary": {
            "catalog_monsters": len(ready_names) + len(blockers_by_name),
            "ready": len(ready_names),
            "blocked": len(blockers_by_name),
            "blocker_families": len(incidence),
            "unclassified_source_defects": len(unclassified),
        },
        "families": [
            {"id": family, "count": len(names), "monsters": names}
            for family, names in incidence.items()
        ],
        "unclassified_source_defects": unclassified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export structured 2024 monster mechanic blockers.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(_payload(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"Monster mechanic inventory is stale: {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
    else:
        OUTPUT.write_text(rendered, encoding="utf-8")
    payload = json.loads(rendered)
    summary = payload["summary"]
    print(
        "MONSTER_MECHANIC_INVENTORY"
        f" ready={summary['ready']}"
        f" blocked={summary['blocked']}"
        f" families={summary['blocker_families']}"
        f" unclassified={summary['unclassified_source_defects']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
