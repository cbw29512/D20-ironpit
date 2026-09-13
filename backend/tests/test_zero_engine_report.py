from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "scripts" / "report_zero_engine_monsters.py"


def _load_report_module():
    spec = importlib.util.spec_from_file_location("report_zero_engine_monsters", REPORT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_modeled_flat_extra_damage_is_not_reported_as_unsupported_rider() -> None:
    report = _load_report_module()
    actions = (
        "Ritual Sickle. Melee Attack Roll: +3, reach 5 ft. "
        "Hit: 3 (1d4 + 1) Slashing damage plus 1 Necrotic damage."
    )

    assert report._unmodeled_action_rider(actions) is False


def test_unmodeled_attach_rider_still_fails_closed() -> None:
    report = _load_report_module()
    actions = (
        "Proboscis. Melee Attack Roll: +5, reach 5 ft. "
        "Hit: 5 (1d4 + 3) Piercing damage, and the creature attaches to the target."
    )

    assert report._unmodeled_action_rider(actions) is True
