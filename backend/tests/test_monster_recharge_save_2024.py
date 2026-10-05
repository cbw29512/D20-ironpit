from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from app.content.monster_catalog import load_monster_rows
from app.content.monster_recharge_save_2024 import (
    compile_recharge_save_bindings,
    recharge_save_coverage_matches,
)
from report_zero_engine_monsters import _source_blockers
from verify_certification_manifests import _detected_monster_mechanics


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_ankheg_recharge_save_compiles_resource_and_threshold() -> None:
    binding = compile_recharge_save_bindings(_row("Ankheg"))[0]

    assert binding.source_name == "actions:Acid Spray (Recharge 6)"
    assert binding.action.name == "Acid Spray"
    assert binding.action.resource_id == "acid-spray"
    assert binding.resource.id == "acid-spray"
    assert binding.resource.max_uses == 1
    assert binding.recharge_rule.resource_id == "acid-spray"
    assert binding.recharge_rule.minimum_roll == 6
    assert binding.recharge_rule.die_size == 6


def test_winter_wolf_recharge_five_to_six_uses_minimum_five() -> None:
    binding = compile_recharge_save_bindings(_row("Winter Wolf"))[0]

    assert binding.action.name == "Cold Breath"
    assert binding.recharge_rule.minimum_roll == 5


def test_mixed_or_non_save_limited_use_stays_fail_closed() -> None:
    names = {str(row["name"]) for row in load_monster_rows()}

    for monster in ("Adult Black Dragon", "Ape", "Doppelganger"):
        assert not recharge_save_coverage_matches(_row(monster))
        assert "limited-use" in _source_blockers(_row(monster), names)


def test_supported_recharge_stays_detected_in_manifest() -> None:
    row = _row("Ankheg")
    names = {str(item["name"]) for item in load_monster_rows()}
    blockers = _source_blockers(row, names)
    detected = _detected_monster_mechanics(row, blockers)

    assert "limited-use" in detected
    assert "limited-use" not in blockers


def test_recharge_save_batch_matches_expected_current_yield() -> None:
    rows = load_monster_rows()
    names = {str(row["name"]) for row in rows}
    cleared = {
        str(row["name"])
        for row in rows
        if recharge_save_coverage_matches(row)
        and "limited-use" not in _source_blockers(row, names)
    }
    expected = {
        "Ankheg",
        "Behir",
        "Brass Dragon Wyrmling",
        "Bronze Dragon Wyrmling",
        "Chimera",
        "Copper Dragon Wyrmling",
        "Dragon Turtle",
        "Gold Dragon Wyrmling",
        "Iron Golem",
        "Magma Mephit",
        "Silver Dragon Wyrmling",
        "Storm Giant",
        "Winter Wolf",
        "Young Brass Dragon",
        "Young Bronze Dragon",
        "Young Copper Dragon",
        "Young Gold Dragon",
        "Young Silver Dragon",
    }

    assert cleared == expected
