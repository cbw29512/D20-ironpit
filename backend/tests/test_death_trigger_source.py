from __future__ import annotations

import sys
from pathlib import Path

import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_death_trigger_source import parse_death_trigger_effects
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from browser_template_serializer import template_row  # noqa: E402


_EXPECTED = {
    "Dust Mephit": ("dexterity", 10, 5, 2, 4, 0, "bludgeoning"),
    "Ice Mephit": ("constitution", 10, 5, 2, 4, 0, "cold"),
    "Magma Mephit": ("dexterity", 11, 5, 2, 6, 0, "fire"),
    "Magmin": ("dexterity", 11, 10, 2, 6, 0, "fire"),
    "Steam Mephit": ("dexterity", 10, 5, 2, 4, 0, "fire"),
}


def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def test_canonical_death_bursts_parse_to_one_universal_data_shape() -> None:
    rows = _rows_by_name()
    for name, expected in _EXPECTED.items():
        effects = parse_death_trigger_effects(rows[name]["traits"])
        assert len(effects) == 1
        effect = effects[0]
        actual = (
            effect.save_ability,
            effect.dc,
            effect.radius_ft,
            effect.damage_dice_count,
            effect.damage_dice_size,
            effect.damage_bonus,
            effect.damage_type.value,
        )
        assert actual == expected
        assert effect.id == "death-burst"
        assert effect.half_damage_on_success is True


def test_unknown_death_burst_wording_fails_closed() -> None:
    with pytest.raises(ValueError, match="not supported"):
        parse_death_trigger_effects("Death Burst. The creature explodes when it dies in a strange unmodeled way.")


def test_roster_binds_death_burst_data_without_claiming_runtime_certification() -> None:
    rows = _rows_by_name()
    roster = {template.name: template for template in build_arena_roster().monsters}
    for name in _EXPECTED:
        template = roster[name]
        assert len(template.death_trigger_effects) == 1
        issues = audit_monster_source(template, rows[name])
        assert "death-trigger-source-data-mismatch" not in issues
        assert "uncertified-trait:death-burst" in issues


def test_browser_template_serializes_the_same_death_trigger_contract() -> None:
    magma = next(template for template in build_arena_roster().monsters if template.name == "Magma Mephit")
    row = template_row(magma)
    assert row["death_trigger_effects"] == [{
        "id": "death-burst",
        "name": "Death Burst",
        "radius_ft": 5,
        "save_ability": "dexterity",
        "dc": 11,
        "damage_dice_count": 2,
        "damage_dice_size": 6,
        "damage_bonus": 0,
        "damage_type": "fire",
        "half_damage_on_success": True,
    }]
