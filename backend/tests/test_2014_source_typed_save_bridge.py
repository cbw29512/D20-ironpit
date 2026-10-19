"""2014 source-owned saving-throw cards preserve typed effects and target limits."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from app.content.capability_compiler import _compile_save
from app.content.monster_save_capabilities_2014 import (
    save_capabilities_2014,
    supports_save_action_2014,
    unsupported_save_actions_2014,
)
from app.content.monster_source_2014 import SourceMonster2014

_scripts = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from browser_template_serializer import _save


def _action(name: str = "Unrelated Homebrew Action") -> dict:
    return {
        "id": "synthetic-area-save", "name": name,
        "save_ability": "dexterity", "dc": 16, "range_ft": 15,
        "max_targets": 4, "success_damage": "half",
        "damage_components": [
            {"dice_count": 3, "dice_size": 6, "damage_bonus": 4, "damage_type": "bludgeoning"},
            {"dice_count": 3, "dice_size": 6, "damage_bonus": 4, "damage_type": "slashing"},
        ],
    }


def _source(action: dict) -> SourceMonster2014:
    return SourceMonster2014(
        id="synthetic-source", name="Synthetic Source", ruleset="2014",
        size="Medium", creature_type="humanoid", armor_class=13, max_hp=20,
        speed={"walk": 30}, abilities={}, saving_throw_actions=[action],
        action_names=[action["name"]],
    )


@pytest.mark.parametrize("name", ["Unrelated Homebrew Action", "Other Printed Action"])
def test_source_to_python_and_browser_preserves_typed_damage_and_targets(name: str) -> None:
    source = _source(_action(name))
    assert unsupported_save_actions_2014(source) == []
    card = save_capabilities_2014(source)[0]
    compiled = _compile_save(card)
    browser = _save(compiled)
    assert compiled.name == name and compiled.max_targets == 4
    assert [(item.damage_type, item.dice_count, item.damage_bonus)
            for item in compiled.damage_components] == [
        ("bludgeoning", 3, 4), ("slashing", 3, 4),
    ]
    assert browser["name"] == name and browser["maxTargets"] == 4
    assert [(item["damageType"], item["diceCount"], item["damageBonus"])
            for item in browser["damageComponents"]] == [
        ("bludgeoning", 3, 4), ("slashing", 3, 4),
    ]


@pytest.mark.parametrize("mutation", [
    {"damage_dice_count": 1, "damage_type": "fire"},
    {"max_targets": 0}, {"max_targets": 21}, {"max_targets": True},
    {"damage_components": [{"dice_count": 2, "damage_type": "invalid"}]},
    {"damage_components": "not a list"},
])
def test_malformed_source_actions_fail_closed(mutation: dict) -> None:
    action = _action()
    action.update(mutation)
    assert not supports_save_action_2014(action)
    assert unsupported_save_actions_2014(_source(action)) == [action]


def test_legacy_single_type_action_keeps_default_target_count() -> None:
    action = _action()
    action.pop("damage_components")
    action.pop("max_targets")
    action.update(damage_dice_count=2, damage_dice_size=6, damage_type="fire")
    compiled = _compile_save(save_capabilities_2014(_source(action))[0])
    assert compiled.max_targets == 1
    assert compiled.damage_dice_count == 2 and compiled.damage_components == []
    assert "maxTargets" not in _save(compiled)
