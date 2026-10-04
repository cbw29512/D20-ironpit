from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.pregen_2014_roster_audit import (  # noqa: E402
    EXPECTED_2014_SNAPSHOTS,
    audit_2014_pregen_roster,
)


def _print_report(rows) -> int:
    passed = [row for row in rows if row.passed]
    failed = [row for row in rows if not row.passed]
    by_class: dict[str, list] = defaultdict(list)
    mechanic_counts: Counter[str] = Counter()
    for row in rows:
        by_class[row.class_id].append(row)
        mechanic_counts.update(row.unsupported_mechanics)

    print("2014 PREGEN ROSTER AUDIT")
    print("This is a batch RAW + engine-support check, not a certification stamp.")
    print(f"checked={len(rows)}/{EXPECTED_2014_SNAPSHOTS} passed={len(passed)} failed={len(failed)}")
    print()
    print("By class:")
    for class_id in sorted(by_class):
        class_rows = by_class[class_id]
        class_pass = sum(row.passed for row in class_rows)
        print(f"- {class_id}: {class_pass}/{len(class_rows)} pass")
    if failed:
        print()
        print("Failures:")
        for row in failed:
            mechanics = "; ".join(row.unsupported_mechanics) or "unknown"
            label = row.hero_name or row.class_id
            print(f"- FAIL {label} {row.class_id} {row.level}: {mechanics}")
        print()
        print("Unsupported mechanic families:")
        families: Counter[str] = Counter()
        for mechanic, count in mechanic_counts.items():
            families[mechanic.split(":", 1)[0]] += count
        for family, count in families.most_common():
            print(f"- {family}: {count}")
        print()
        print("Unique unsupported mechanics:")
        for mechanic, count in mechanic_counts.most_common():
            print(f"- {mechanic} ({count} snapshot(s))")
    return 0 if not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-check every 2014 canonical pregen against RAW build rules and engine bindings."
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable snapshot results.")
    args = parser.parse_args()
    rows = audit_2014_pregen_roster()
    if args.json:
        print(json.dumps(
            [
                {
                    "class_id": row.class_id,
                    "hero_name": row.hero_name,
                    "level": row.level,
                    "template_id": row.template_id,
                    "checked": row.checked,
                    "passed": row.passed,
                    "unsupported_mechanics": list(row.unsupported_mechanics),
                }
                for row in rows
            ],
            indent=2,
        ))
        return 0 if all(row.passed for row in rows) else 1
    return _print_report(rows)


if __name__ == "__main__":
    raise SystemExit(main())
