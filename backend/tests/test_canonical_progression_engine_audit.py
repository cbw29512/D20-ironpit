from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "export_canonical_progression_engine_audit.py"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("canonical_progression_engine_audit", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load progression audit script from {SCRIPT}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_arena_out_of_scope_status_is_nonblocking() -> None:
    audit = _load_audit_module()

    assert audit._is_blocking("supported") is False
    assert audit._is_blocking("arena_out_of_scope") is False
    assert audit._is_blocking("planned") is True
    assert audit._is_blocking("partial") is True
    assert audit._is_blocking("unsupported") is True


def test_bardic_inspiration_does_not_block_solo_arena_level_one() -> None:
    audit = _load_audit_module()
    payload = audit._payload()
    bard = next(item for item in payload["classes"] if item["class_id"] == "bard")
    level_one = bard["levels"][0]

    bardic = next(row for row in level_one["introduced_combat_features"] if row["id"] == "bardic-inspiration")
    assert bardic["status"] == "arena_out_of_scope"
    assert bardic not in level_one["blockers"]
    assert bard["level_1_engine_ready"] is True
