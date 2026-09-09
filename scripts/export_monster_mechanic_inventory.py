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
from app.content.monster_mechanic_detail_inventory import (  # noqa: E402
    complex_action_incidence,
    control_effect_incidence,
    unsupported_trait_incidence,
)
from app.content.monster_mechanic_family_registry import MONSTER_MECHANIC_FAMILIES  # noqa: E402


def _subfamilies(rows_by_name: dict[str, dict[str, object]], incidence: dict[str, list[str]]) -> dict[str, object]:
    return {
        "trait_headings": unsupported_trait_incidence(rows_by_name, incidence.get("trait", [])),
        "control_effects": control_effect_incidence(rows_by_name, incidence.get("condition-or-control", [])),
        "complex_action_kinds": complex_action_incidence(rows_by_name, incidence.get("save-or-complex-action", [])),
    }


def _payload() -> dict[str, object]:
    rows_by_name, ready_names, blockers_by_name = build_monster_blocker_inventory()
    incidence = blocker_family_incidence(blockers_by_name)
    missing_registry = sorted(set(incidence) - set(MONSTER_MECHANIC_FAMILIES))
    if missing_registry:
        raise ValueError(f"Unclassified blocker families: {', '.join(missing_registry)}")
    unclassified = sorted(
        name
        for name, blockers in blockers_by_name.items()
        if "unclassified-source-audit-gap" in blockers
    )
    families = []
    for family, names in incidence.items():
        layer = MONSTER_MECHANIC_FAMILIES[family]
        families.append({"id": family, "count": len(names), "monsters": names, **layer})
    return {
        "schema_version": 3,
        "ruleset": "srd-5.2.1-2024",
        "summary": {
            "catalog_monsters": len(ready_names) + len(blockers_by_name),
            "ready": len(ready_names),
            "blocked": len(blockers_by_name),
            "blocker_families": len(incidence),
            "unclassified_source_defects": len(unclassified),
            "unregistered_families": len(missing_registry),
        },
        "families": families,
        "subfamilies": _subfamilies(rows_by_name, incidence),
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
        f" unregistered={summary['unregistered_families']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
