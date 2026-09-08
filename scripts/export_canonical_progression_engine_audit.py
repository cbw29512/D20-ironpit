from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MATRIX = ROOT / "data" / "combat_engine_coverage_v1.json"
OUTPUT = ROOT / "data" / "canonical_progression_engine_audit.json"
sys.path.insert(0, str(BACKEND))

from app.content.canonical_class_combat_spines import (  # noqa: E402
    CANONICAL_CLASS_COMBAT_SPINES,
    canonical_combat_features,
)
from app.content.class_subclass_composer import base_class_arena_ignored  # noqa: E402
from app.content.hero_combat_feature_registry import SUPPORTED_HERO_FEATURES  # noqa: E402
from app.content.hero_progressions import CANONICAL_HEROES  # noqa: E402
from app.content.subclass_combat_overlays import subclass_overlay  # noqa: E402


NON_BLOCKING_STATUSES = frozenset({"supported", "arena_out_of_scope"})


def _status(feature_id: str, statuses: dict[str, str]) -> str:
    if feature_id in SUPPORTED_HERO_FEATURES:
        return "supported"
    if feature_id in statuses:
        return statuses[feature_id]
    return "planned"


def _effective_status(feature_id: str, statuses: dict[str, str], arena_ignored: set[str]) -> str:
    """Resolve audit status, giving canonical arena-exclusion metadata precedence."""
    if feature_id in arena_ignored:
        return "arena_out_of_scope"
    return _status(feature_id, statuses)


def _is_blocking(status: str) -> bool:
    """Return whether a capability status prevents an arena snapshot from certifying."""
    return status not in NON_BLOCKING_STATUSES


def _ignored_at_level(class_id: str, subclass_id: str, level: int) -> list[str]:
    rows = CANONICAL_CLASS_COMBAT_SPINES[class_id]
    base = set(base_class_arena_ignored(class_id, level, rows))
    prior = set(base_class_arena_ignored(class_id, level - 1, rows)) if level > 1 else set()
    current = base - prior
    delta = subclass_overlay(subclass_id).deltas.get(level)
    if delta:
        current.update(delta.arena_ignored)
    return sorted(current)


def _payload() -> dict[str, object]:
    coverage = json.loads(MATRIX.read_text(encoding="utf-8"))
    statuses = {item["id"]: item["status"] for item in coverage["capabilities"]}
    all_features: set[str] = set()
    effective_statuses: dict[str, str] = {}
    blocker_features: dict[str, str] = {}
    classes: list[dict[str, object]] = []

    for hero in CANONICAL_HEROES:
        previous: set[str] = set()
        levels: list[dict[str, object]] = []
        first_blocked_level: int | None = None
        for level in range(1, 21):
            active = set(canonical_combat_features(hero.class_id, level, hero.subclass_id))
            introduced = sorted(active - previous)
            ignored_introduced = set(_ignored_at_level(hero.class_id, hero.subclass_id, level))
            feature_rows = [
                {"id": item, "status": _effective_status(item, statuses, ignored_introduced)}
                for item in introduced
            ]
            blockers = [row for row in feature_rows if _is_blocking(str(row["status"]))]
            if blockers and first_blocked_level is None:
                first_blocked_level = level
            for row in feature_rows:
                feature_id = str(row["id"])
                feature_status = str(row["status"])
                all_features.add(feature_id)
                effective_statuses[feature_id] = feature_status
                if _is_blocking(feature_status):
                    blocker_features[feature_id] = feature_status
            levels.append({
                "level": level,
                "introduced_combat_features": feature_rows,
                "arena_ignored_introduced": sorted(ignored_introduced),
                "blockers": blockers,
            })
            previous = active
        classes.append({
            "class_id": hero.class_id,
            "hero_name": hero.hero_name,
            "subclass_id": hero.subclass_id,
            "first_blocked_level": first_blocked_level,
            "level_1_engine_ready": first_blocked_level != 1,
            "levels": levels,
        })

    status_counts = Counter(effective_statuses[feature_id] for feature_id in all_features)
    return {
        "schema_version": 1,
        "ruleset": "srd-5.2.1-2024",
        "purpose": "Audit the 12 canonical pregens from level 1 through 20 against universal Iron Pit combat mechanics.",
        "summary": {
            "canonical_classes": len(CANONICAL_HEROES),
            "level_slots": len(CANONICAL_HEROES) * 20,
            "unique_combat_features": len(all_features),
            "level_1_engine_ready_classes": sum(item["level_1_engine_ready"] for item in classes),
            "feature_statuses": dict(sorted(status_counts.items())),
            "unique_blocking_features": len(blocker_features),
        },
        "blocking_features": [
            {"id": feature_id, "status": blocker_features[feature_id]}
            for feature_id in sorted(blocker_features)
        ],
        "classes": classes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit all 12 canonical pregens through level 20.")
    parser.add_argument("--check", action="store_true", help="Fail if the committed audit is stale.")
    args = parser.parse_args()
    payload = _payload()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"Canonical progression audit is stale: {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
    else:
        OUTPUT.write_text(rendered, encoding="utf-8")
    print("CANONICAL_PROGRESSION_AUDIT " + " ".join(f"{key}={value}" for key, value in payload["summary"].items()))
    for item in payload["classes"]:
        first = item["first_blocked_level"] if item["first_blocked_level"] is not None else "none"
        blocker_ids = "none"
        if item["first_blocked_level"] is not None:
            first_row = item["levels"][item["first_blocked_level"] - 1]
            blocker_ids = ",".join(row["id"] for row in first_row["blockers"]) or "none"
        print(f"CANONICAL_CLASS_AUDIT class={item['class_id']} level1_ready={item['level_1_engine_ready']} first_blocked_level={first} blockers={blocker_ids}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
