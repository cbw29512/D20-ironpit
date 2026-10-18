"""Live 2014 blocker snapshot and fail-closed monster progress checks.

Uses the same classifier as the generated roster; never infers battle readiness.
Run: python scripts/check_2014_monster_progress.py --output /tmp/before.json
After edits: python scripts/check_2014_monster_progress.py --baseline /tmp/before.json --require-unblocked basilisk
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014


def snapshot() -> dict:
    monsters = load_monster_source_2014()
    blocked = {
        monster.id: list(basic_blockers_2014(monster))
        for monster in monsters if basic_blockers_2014(monster)
    }
    families = Counter(code for codes in blocked.values() for code in codes)
    return {
        "schema": 1,
        "total": len(monsters),
        "admitted": len(monsters) - len(blocked),
        "blocked": len(blocked),
        "families": dict(sorted(families.items(), key=lambda v: (-v[1], v[0]))),
        "monsters": blocked,
    }


def compare(before: dict, after: dict, required: list[str], forbid_regressions: bool = True) -> dict:
    if before.get("schema") != 1 or before.get("total") != after["total"]:
        raise ValueError("Invalid or incompatible baseline snapshot")
    old = before.get("monsters")
    if not isinstance(old, dict) or any(
        not isinstance(k, str) or not isinstance(v, list) for k, v in old.items()
    ):
        raise ValueError("Invalid monster baseline")
    current = after["monsters"]
    unblocked = sorted(set(old) - set(current))
    newly_blocked = sorted(set(current) - set(old))
    changed = {
        key: {"before": old[key], "after": current[key]}
        for key in sorted(set(old) & set(current)) if old[key] != current[key]
    }
    if forbid_regressions and newly_blocked:
        raise ValueError(f"Previously admitted monsters became blocked: {newly_blocked}")
    missing = sorted(set(required) - set(unblocked))
    if missing:
        raise ValueError(f"Claimed monster admissions not achieved: {missing}")
    return {
        "admitted_delta": after["admitted"] - before["admitted"],
        "blocked_delta": after["blocked"] - before["blocked"],
        "unblocked": unblocked,
        "newly_blocked": newly_blocked,
        "changed_blockers": changed,
        "battle_tested": "not measured by source admission",
    }



def next_work(state: dict, limit: int = 5) -> list[dict]:
    """Rank actionable single-blocker families without pretending they are implemented."""
    excluded = {"arena:neutral", "arena:removed"}
    singles: dict[str, list[str]] = {}
    for monster_id, blockers in state["monsters"].items():
        if len(blockers) == 1 and blockers[0] not in excluded:
            singles.setdefault(blockers[0], []).append(monster_id)
    return [
        {"family": family, "monsters": sorted(ids), "potential_admissions": len(ids)}
        for family, ids in sorted(
            singles.items(), key=lambda pair: (-len(pair[1]), pair[0])
        )[:limit]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--next", action="store_true", help="Show ranked single-blocker work families")
    parser.add_argument("--output", type=Path, help="Write machine-readable baseline/current snapshot")
    parser.add_argument("--baseline", type=Path, help="Compare with previously saved snapshot")
    parser.add_argument("--require-unblocked", action="append", default=[], metavar="MONSTER_ID")
    args = parser.parse_args()
    state = snapshot()
    if args.require_unblocked and not args.baseline:
        parser.error("--require-unblocked requires --baseline")
    result = {"snapshot": state}
    if args.next:
        result["next_work"] = next_work(state)
    if args.baseline:
        result["progress"] = compare(
            json.loads(args.baseline.read_text(encoding="utf-8")),
            state, args.require_unblocked,
        )
    if args.output:
        args.output.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
