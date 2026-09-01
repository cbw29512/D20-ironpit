from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data" / "combat_engine_coverage_v1.json"
VALID_STATUSES = {"supported", "partial", "unsupported", "arena_out_of_scope"}


def _require_file(path: str, capability_id: str) -> None:
    target = ROOT / path
    if not target.is_file():
        raise SystemExit(f"Combat coverage {capability_id!r} cites missing evidence: {path}")


def main() -> None:
    payload = json.loads(MATRIX.read_text(encoding="utf-8"))
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise SystemExit("Combat coverage matrix must contain a non-empty capabilities list.")

    seen: set[str] = set()
    statuses: Counter[str] = Counter()
    for item in capabilities:
        capability_id = str(item.get("id", "")).strip()
        status = str(item.get("status", "")).strip()
        if not capability_id or capability_id in seen:
            raise SystemExit(f"Combat coverage capability IDs must be unique and non-empty: {capability_id!r}")
        seen.add(capability_id)
        if status not in VALID_STATUSES:
            raise SystemExit(f"Combat coverage {capability_id!r} has invalid status {status!r}.")
        statuses[status] += 1

        if status == "supported":
            for field in ("python", "browser", "tests"):
                evidence = item.get(field)
                if not isinstance(evidence, list) or not evidence:
                    raise SystemExit(f"Supported capability {capability_id!r} lacks {field} evidence.")
                for path in evidence:
                    _require_file(str(path), capability_id)
        elif not str(item.get("blocker", "")).strip():
            raise SystemExit(f"Non-supported capability {capability_id!r} must name its blocker or scope reason.")

    print(
        "COMBAT_ENGINE_COVERAGE"
        f"\ttotal={len(capabilities)}\tsupported={statuses['supported']}"
        f"\tpartial={statuses['partial']}\tunsupported={statuses['unsupported']}"
        f"\tarena_out_of_scope={statuses['arena_out_of_scope']}"
    )


if __name__ == "__main__":
    main()
