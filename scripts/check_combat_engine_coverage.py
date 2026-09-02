from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MATRIX = ROOT / "data" / "combat_engine_coverage_v1.json"
VALID_STATUSES = {"supported", "blocked", "partial", "unsupported", "arena_out_of_scope"}

sys.path.insert(0, str(BACKEND))
from app.content.combat_engine_coverage import audit_current_build_capabilities  # noqa: E402

logger = logging.getLogger(__name__)


def _require_file(path: str, capability_id: str) -> None:
    target = ROOT / path
    if not target.is_file():
        raise ValueError(f"Combat coverage {capability_id!r} cites missing evidence: {path}")


def _validate_matrix(payload: object) -> tuple[list[dict[str, object]], Counter[str], dict[str, str]]:
    if not isinstance(payload, dict):
        raise ValueError("Combat coverage matrix root must be an object.")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise ValueError("Combat coverage matrix must contain a non-empty capabilities list.")

    seen: set[str] = set()
    statuses: Counter[str] = Counter()
    status_by_id: dict[str, str] = {}
    for raw_item in capabilities:
        if not isinstance(raw_item, dict):
            raise ValueError("Every combat coverage capability must be an object.")
        item = raw_item
        capability_id = str(item.get("id", "")).strip()
        status = str(item.get("status", "")).strip()
        if not capability_id or capability_id in seen:
            raise ValueError(f"Combat coverage capability IDs must be unique and non-empty: {capability_id!r}")
        seen.add(capability_id)
        if status not in VALID_STATUSES:
            raise ValueError(f"Combat coverage {capability_id!r} has invalid status {status!r}.")
        statuses[status] += 1
        status_by_id[capability_id] = status

        if status == "supported":
            for field in ("python", "browser", "tests"):
                evidence = item.get(field)
                if not isinstance(evidence, list) or not evidence:
                    raise ValueError(f"Supported capability {capability_id!r} lacks {field} evidence.")
                for path in evidence:
                    _require_file(str(path), capability_id)
        elif not str(item.get("blocker", "")).strip():
            raise ValueError(f"Non-supported capability {capability_id!r} must name its blocker or scope reason.")
    return capabilities, statuses, status_by_id


def main() -> int:
    try:
        payload = json.loads(MATRIX.read_text(encoding="utf-8"))
        capabilities, statuses, status_by_id = _validate_matrix(payload)
        if isinstance(payload, dict) and payload.get("build_contract_version") == 1:
            build_issues = audit_current_build_capabilities(status_by_id)
            if build_issues:
                raise ValueError("Combat build capability contract failed:\n- " + "\n- ".join(build_issues))
        print(
            "COMBAT_ENGINE_COVERAGE"
            f"\ttotal={len(capabilities)}\tsupported={statuses['supported']}"
            f"\tblocked={statuses['blocked']}\tpartial={statuses['partial']}"
            f"\tunsupported={statuses['unsupported']}"
            f"\tarena_out_of_scope={statuses['arena_out_of_scope']}"
        )
        return 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError, RuntimeError) as exc:
        logger.error("Combat engine coverage validation failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
