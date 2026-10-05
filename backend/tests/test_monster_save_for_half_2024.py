from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from app.content.monster_catalog import load_monster_rows
from app.content.monster_save_for_half_2024 import compile_save_for_half_actions, compiled_save_signatures
from app.content.monster_source_audit import _source_save_signatures
from report_zero_engine_monsters import _source_blockers


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_adult_black_dragon_breath_compiles_from_source() -> None:
    action = compile_save_for_half_actions(_row("Adult Black Dragon"))[0]

    assert action.name == "Acid Breath"
    assert action.save_ability == "dexterity"
    assert action.dc == 18
    assert action.range_ft == 60
    assert action.area is not None
    assert action.area.shape == "line"
    assert action.area.length_ft == 60
    assert action.area.width_ft == 5
    assert (action.damage_dice_count, action.damage_dice_size, action.damage_bonus) == (12, 8, 0)
    assert action.damage_type == "acid"
    assert action.success_damage == "half"
    assert action.resource_id == "acid-breath"


def test_planetar_holy_burst_compiles_point_radius_geometry() -> None:
    action = compile_save_for_half_actions(_row("Planetar"))[0]

    assert action.name == "Holy Burst"
    assert action.range_ft == 120
    assert action.area is not None
    assert action.area.shape == "radius"
    assert action.area.origin == "point"
    assert action.area.radius_ft == 20
    assert action.damage_type == "radiant"


def test_all_source_saves_must_be_simple_before_save_blocker_clears() -> None:
    copper = _row("Copper Dragon Wyrmling")
    adult_black = _row("Adult Black Dragon")
    names = {str(row["name"]) for row in load_monster_rows()}

    assert compiled_save_signatures(adult_black) == _source_save_signatures(str(adult_black["actions"]))
    assert "save-or-complex-action" not in _source_blockers(adult_black, names)

    assert compiled_save_signatures(copper) != _source_save_signatures(str(copper["actions"]))
    assert "save-or-complex-action" in _source_blockers(copper, names)


def test_compiler_covers_large_repeated_source_family() -> None:
    compiled = {
        str(row["name"]): compile_save_for_half_actions(row)
        for row in load_monster_rows()
    }
    action_count = sum(len(actions) for actions in compiled.values())

    assert action_count >= 43
    assert sum(bool(actions) for actions in compiled.values()) >= 39


def test_grapple_prerequisite_save_stays_out_of_simple_compiler() -> None:
    glabrezu = _row("Glabrezu")
    names = {str(row["name"]) for row in load_monster_rows()}

    assert compile_save_for_half_actions(glabrezu) == []
    assert "save-or-complex-action" in _source_blockers(glabrezu, names)
