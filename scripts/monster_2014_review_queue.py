#!/usr/bin/env python3
"""Read the 2014 monster planning state without re-opening settled decisions.

This is a planning/read-only helper. It does not implement monster effects,
change source records, schedule tasks, publish the arena, or infer user questions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "monster_2014_review_state.json"
ALLOWED_STATES = frozenset({"decision_complete", "partial", "needs_source_review"})


def load() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    entries = data["monsters"]
    assert len(entries) == 124, "Expected the pinned 124-monster planning roster"
    assert [m["number"] for m in entries] == list(range(1, 125)), "Order or IDs drifted"
    assert len({m["name"] for m in entries}) == 124, "Duplicate monster names"
    assert sum(len(m["blocker_categories"]) for m in entries) == 305, "Source blocker snapshot drifted"
    for m in entries:
        assert m["planning_state"] in ALLOWED_STATES, (m["name"], m["planning_state"])
        assert isinstance(m["recorded_decisions"], list)
        assert isinstance(m["carried_over_notes"], list)
        assert isinstance(m["open_user_questions"], list)
        assert isinstance(m["pending_source_review"], list)
        if m["planning_state"] == "decision_complete":
            assert not m["pending_source_review"], f"Settled monster cannot be queued for repeat review: {m['name']}"
    assert 1 <= data["review_cursor_number"] <= len(entries)
    return data


def sweep(data: dict) -> list[dict]:
    """Resume at stored cursor, wrapping only to genuinely unfinished work."""
    index = data["review_cursor_number"] - 1
    items = data["monsters"]
    return items[index:] + items[:index]


def next_source_review(data: dict) -> dict | None:
    for entry in sweep(data):
        if entry["planning_state"] != "decision_complete":
            return {
                "number": entry["number"],
                "monster": entry["name"],
                "planning_state": entry["planning_state"],
                "next_source_audit": entry["pending_source_review"][0]
                if entry["pending_source_review"] else "Inspect remaining source clauses",
                "already_recorded_decisions": entry["recorded_decisions"],
                "carried_over_notes": entry["carried_over_notes"],
                "user_question": None,
                "instruction": "Audit the next unreviewed source behavior, reuse documented rulings, and only create a user question if a new genuine policy conflict is verified.",
            }
    return None


def open_user_questions(data: dict) -> list[dict]:
    """NEVER infer questions from historical blockers, checkboxes, or unmerged PRs."""
    return [
        {"number": m["number"], "monster": m["name"], "question": q}
        for m in sweep(data)
        for q in m["open_user_questions"]
        if q.get("status") == "open"
    ]


def summary(data: dict) -> dict:
    counts = {state: 0 for state in sorted(ALLOWED_STATES)}
    for monster in data["monsters"]:
        counts[monster["planning_state"]] += 1
    return {
        "snapshot_monsters": len(data["monsters"]),
        "source_blocker_categories": sum(len(m["blocker_categories"]) for m in data["monsters"]),
        "planning_states": counts,
        "open_user_questions": len(open_user_questions(data)),
        "next_source_review": (next_source_review(data) or {}).get("monster"),
        "hourly_implementation_started": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--next", action="store_true", help="Show only next genuinely unfinished source audit")
    group.add_argument("--questions", action="store_true", help="Show only actual recorded, open user decisions")
    group.add_argument("--verify", action="store_true", help="Validate all 124 states and historical blocker count")
    args = parser.parse_args()
    data = load()
    result = (
        next_source_review(data) if args.next else
        open_user_questions(data) if args.questions else
        {"valid": True, **summary(data)} if args.verify else
        summary(data)
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
