from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "monster_certification_manifest.json"
GATES = ROOT / "data" / "combat_refactor_gates_v1.json"


def _percent(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100.0, 1) if denominator else 0.0


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    gates = json.loads(GATES.read_text(encoding="utf-8"))

    ready = int(manifest["summary"]["public_ready"])
    total = int(manifest["summary"]["catalog_monsters"])
    blocked = int(manifest["summary"]["blocked"])
    phases = gates["phases"]
    passed = sum(1 for phase in phases if phase["status"] == "passed")

    monster_percent = _percent(ready, total)
    refactor_percent = _percent(passed, len(phases))
    overall_percent = round((monster_percent + refactor_percent) / 2.0, 1)

    print(
        "IRON_PIT_COMPLETION"
        f" monsters={ready}/{total}"
        f" monster_percent={monster_percent:.1f}"
        f" blocked={blocked}"
        f" refactor_gates={passed}/{len(phases)}"
        f" refactor_percent={refactor_percent:.1f}"
        f" overall_percent={overall_percent:.1f}"
        f" status={'COMPLETE' if ready == total and passed == len(phases) else 'IN_PROGRESS'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
