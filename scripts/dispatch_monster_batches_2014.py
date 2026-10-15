"""Source-owned 2014 monster batch dispatcher; never changes combat eligibility.

Run again after each certified merge. Every run reads the live source classifier,
regroups remaining blockers, and promotes the next highest-yield semantic family.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)
POLICY_ONLY = frozenset({"arena:removed", "arena:neutral"})


def current_state(monsters=None):
    """Recompute from immutable source, not a stale manually edited tracker."""
    try:
        source = load_monster_source_2014() if monsters is None else monsters
        blocked = {m.id: {"name": m.name, "blockers": sorted(set(basic_blockers_2014(m)))}
                   for m in source if basic_blockers_2014(m)}
        return {"total": len(source), "admitted": len(source) - len(blocked),
                "blocked": blocked}
    except Exception:
        logger.exception("2014 monster classification failed; refusing stale batch selection.")
        raise


def rank_batches(state):
    """Prioritize shared capability families and monsters one fix from admission."""
    try:
        families = defaultdict(list)
        for mid, entry in state["blocked"].items():
            for category in entry["blockers"]:
                if category not in POLICY_ONLY:
                    families[category].append((mid, entry))
        batches = []
        for category, affected in families.items():
            immediate = [mid for mid, entry in affected if len(entry["blockers"]) == 1]
            near = [mid for mid, entry in affected if len(entry["blockers"]) == 2]
            batches.append({
                "family": category, "affected_monsters": len(affected),
                "immediate_admission_candidates": sorted(immediate),
                "two_blocker_candidates": sorted(near),
                "monster_ids": sorted(mid for mid, _ in affected),
            })
        return sorted(batches, key=lambda x: (
            -len(x["immediate_admission_candidates"]),
            -len(x["two_blocker_candidates"]),
            -x["affected_monsters"], x["family"]
        ))
    except Exception:
        logger.exception("Failed to build 2014 semantic-family batches.")
        raise


def compare(before, after):
    """Never equate a hypothetical batch with resolved source obligations."""
    try:
        old, new = before["blocked"], after["blocked"]
        admitted = sorted(set(old) - set(new))
        regressed = sorted(set(new) - set(old))
        resolved = sorted((mid, blocker) for mid, row in old.items()
                          for blocker in row["blockers"]
                          if blocker not in new.get(mid, {}).get("blockers", []))
        introduced = sorted((mid, blocker) for mid, row in new.items()
                            for blocker in row["blockers"]
                            if blocker not in old.get(mid, {}).get("blockers", []))
        return {"newly_admitted": admitted, "newly_blocked": regressed,
                "resolved_blocker_obligations": resolved,
                "introduced_blocker_obligations": introduced,
                "net_resolved": len(resolved) - len(introduced)}
    except Exception:
        logger.exception("Failed to compare 2014 monster classification snapshots.")
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, help="Write current classification JSON for next merge comparison.")
    parser.add_argument("--compare", type=Path, help="Compare an earlier snapshot to current classification.")
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be positive")
    state = current_state()
    report = {"total": state["total"], "admitted": state["admitted"],
              "blocked": len(state["blocked"]), "next_batches": rank_batches(state)[:args.top],
              "notes": "Candidate counts are not certified completions; implement, test both runtimes, regenerate and merge."}
    if args.compare:
        before = json.loads(args.compare.read_text(encoding="utf-8"))
        report["delta"] = compare(before, state)
        if args.fail_on_regression and (
            report["delta"]["newly_blocked"] or report["delta"]["introduced_blocker_obligations"]
        ):
            raise SystemExit("New 2014 blockers detected; investigate before certification.")
    if args.snapshot:
        args.snapshot.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
