from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

from app.domain.models import CombatantTemplate

_GENERATED_PATH = Path(__file__).with_name("data") / "combatant_capabilities_v1.json"


@lru_cache(maxsize=1)
def generated_legacy_ids() -> frozenset[str]:
    rows = json.loads(_GENERATED_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise RuntimeError("Generated legacy capability registry must be a JSON list.")
    ids = [str(row["id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Generated legacy capability ids must remain unique.")
    return frozenset(ids)


def native_candidate_ids_by_name(runtime: dict[str, CombatantTemplate]) -> dict[str, str]:
    """Anything intentionally added outside the generated legacy registry is audited automatically."""
    legacy_ids = generated_legacy_ids()
    native = [template for template in runtime.values() if template.id not in legacy_ids]
    by_name = {template.name: template.id for template in native}
    if len(by_name) != len(native):
        raise RuntimeError("Native monster certification candidates must have unique names.")
    return by_name
