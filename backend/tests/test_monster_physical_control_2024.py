from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from app.content.monster_catalog import load_monster_rows
from app.content.monster_physical_control_2024 import (
    compile_physical_controls,
    physical_control_coverage_matches,
)
from report_zero_engine_monsters import _source_blockers


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_ankheg_hit_grapple_compiles_exact_source_values() -> None:
    binding = compile_physical_controls(_row("Ankheg"))[0]

    assert binding.action_name == "Bite"
    assert binding.source_kind == "attack"
    assert binding.max_target_size.value == "large"
    assert binding.grapple_escape_dc == 13
    assert not binding.restrains_while_grappled
    assert not binding.knocks_prone


def test_behir_save_grapple_and_restrained_reuse_save_control_primitive() -> None:
    binding = next(
        item for item in compile_physical_controls(_row("Behir"))
        if item.action_name == "Constrict"
    )

    assert binding.source_kind == "save"
    assert binding.save_ability == "strength"
    assert binding.save_dc == 18
    assert binding.max_target_size.value == "large"
    assert binding.grapple_escape_dc == 16
    assert binding.restrains_while_grappled


def test_chimera_unconditional_prone_on_hit_compiles() -> None:
    binding = next(
        item for item in compile_physical_controls(_row("Chimera"))
        if item.action_name == "Ram"
    )

    assert binding.source_kind == "attack"
    assert binding.max_target_size.value == "medium"
    assert binding.knocks_prone


def test_reference_only_condition_words_do_not_create_false_blocker() -> None:
    names = {str(row["name"]) for row in load_monster_rows()}

    for monster in ("Bugbear Stalker", "Sea Hag", "Succubus"):
        assert physical_control_coverage_matches(_row(monster))
        assert "condition-or-control" not in _source_blockers(_row(monster), names)


def test_complex_or_capacity_controls_stay_fail_closed() -> None:
    names = {str(row["name"]) for row in load_monster_rows()}

    for monster in ("Glabrezu", "Elephant", "Fire Giant", "Water Elemental", "Lamia"):
        assert not physical_control_coverage_matches(_row(monster))
        assert "condition-or-control" in _source_blockers(_row(monster), names)


def test_physical_control_batch_has_expected_current_yield() -> None:
    rows = load_monster_rows()
    names = {str(row["name"]) for row in rows}
    cleared = [
        str(row["name"])
        for row in rows
        if "condition-or-control" in _source_blockers(row, names)
        and physical_control_coverage_matches(row)
    ]

    # This expression should remain empty because _source_blockers consumes
    # physical_control_coverage_matches. Recompute against the source marker instead.
    assert cleared == []

    marker_names = {
        str(row["name"])
        for row in rows
        if physical_control_coverage_matches(row)
        and any(
            token in str(row.get("actions", "")).lower()
            for token in ("grappled", "restrained", "prone", "frightened", "charmed")
        )
    }
    expected = {
        "Ankheg", "Behir", "Bugbear Stalker", "Bugbear Warrior", "Chimera",
        "Dragon Turtle", "Ettin", "Giant Ape", "Gladiator", "Marilith",
        "Purple Worm", "Remorhaz", "Salamander", "Sea Hag", "Stone Giant",
        "Succubus", "Winter Wolf",
    }
    assert expected.issubset(marker_names)
