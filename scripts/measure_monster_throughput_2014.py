"""Measure source-owned 2014 ability progress between generated inventory snapshots.

Both JSON inputs must come from recorded repository commits. --hours is actual
work elapsed, not inferred from CI runtimes or guessed from commit timestamps.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
from pathlib import Path

logger = logging.getLogger(__name__)


def unresolved(snapshot: dict) -> set[tuple[str, str]]:
    """Return (monster, printed ability) obligations still requiring support."""
    try:
        # Same-named abilities on different monsters count as separate work.
        rows = snapshot["monster_2014"]["unresolved_printed_abilities"]
        return {
            (monster, row["printed_name"])
            for row in rows
            for monster in row["monsters"]
        }
    except Exception:
        logger.exception("Invalid 2014 inventory snapshot while reading printed abilities.")
        raise


def measure(before: dict, after: dict, hours: float) -> dict:
    """Report resolved and regressed obligations without claiming runtime certification."""
    try:
        # NaN and infinity are invalid even though NaN fails ordinary <= comparisons.
        if not math.isfinite(hours) or hours <= 0:
            raise ValueError("Measured work hours must be finite and positive.")

        old = unresolved(before)
        new = unresolved(after)
        old_blocked = int(before["monster_2014"]["blocked_monster_count"])
        new_blocked = int(after["monster_2014"]["blocked_monster_count"])
        resolved = old - new
        regressions = new - old
        net_admissions = old_blocked - new_blocked

        # "Newly admitted" is a nonnegative count; net throughput may be negative.
        return {
            "elapsed_hours": hours,
            "resolved_printed_ability_obligations": len(resolved),
            "new_unresolved_ability_obligations": len(regressions),
            "net_ability_obligations_resolved": len(resolved) - len(regressions),
            "net_abilities_per_hour": round((len(resolved) - len(regressions)) / hours, 2),
            "gross_abilities_per_hour": round(len(resolved) / hours, 2),
            "newly_source_admitted_monsters": max(0, net_admissions),
            "net_monsters_per_hour": round(net_admissions / hours, 2),
            "resolved": sorted(
                [{"monster": monster, "ability": ability} for monster, ability in resolved],
                key=lambda item: (item["monster"], item["ability"]),
            ),
            "regressions": sorted(
                [{"monster": monster, "ability": ability} for monster, ability in regressions],
                key=lambda item: (item["monster"], item["ability"]),
            ),
        }
    except Exception:
        logger.exception("Failed to measure 2014 monster throughput for %s hours.", hours)
        raise


def main() -> None:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--before", type=Path, required=True)
        parser.add_argument("--after", type=Path, required=True)
        parser.add_argument("--hours", type=float, required=True)
        args = parser.parse_args()

        # Inputs are explicit generated snapshots; never infer a historical baseline.
        before = json.loads(args.before.read_text(encoding="utf-8"))
        after = json.loads(args.after.read_text(encoding="utf-8"))
        print(json.dumps(measure(before, after, args.hours), indent=2))
    except Exception:
        logger.exception("2014 monster throughput CLI failed.")
        raise


if __name__ == "__main__":
    main()
