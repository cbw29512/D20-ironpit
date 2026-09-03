from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MATRIX = ROOT / "data" / "combat_engine_coverage_v1.json"
OUTPUT = ROOT / "data" / "roster_combat_mechanics_v1.json"
sys.path.insert(0, str(BACKEND))

from app.content.hero_variant_policy import TARGET_SUBCLASSES  # noqa: E402
from app.content.roster_mechanic_requirements import derive_roster_mechanic_requirements  # noqa: E402


def _payload() -> dict[str, object]:
    coverage = json.loads(MATRIX.read_text(encoding="utf-8"))
    statuses = {item["id"]: item["status"] for item in coverage["capabilities"]}
    requirements = derive_roster_mechanic_requirements(statuses)
    summary = Counter(item.status for item in requirements)
    return {
        "schema_version": 1,
        "roster": {
            "classes": len(TARGET_SUBCLASSES),
            "subclasses": sum(len(items) for items in TARGET_SUBCLASSES.values()),
        },
        "summary": dict(sorted(summary.items())),
        "mechanics": [
            {
                "id": item.id,
                "kinds": list(item.kinds),
                "owners": list(item.owners),
                "demand_count": item.demand_count,
                "status": item.status,
            }
            for item in requirements
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the mechanic backlog derived from the hero roster.")
    parser.add_argument("--check", action="store_true", help="Fail if the committed checklist is stale.")
    args = parser.parse_args()
    rendered = json.dumps(_payload(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"Roster mechanic checklist is stale: {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
    else:
        OUTPUT.write_text(rendered, encoding="utf-8")
    payload = json.loads(rendered)
    summary = " ".join(f"{key}={value}" for key, value in payload["summary"].items())
    print(f"ROSTER_MECHANICS total={len(payload['mechanics'])} {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
