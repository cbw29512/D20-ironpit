"""2014 Recharge line damage source binding and Python/browser parity."""
from __future__ import annotations

import sys
from pathlib import Path

from app.content.capability_compiler import _compile_save
from app.content.monster_save_capabilities_2014 import (
    save_capabilities_2014,
    save_resources_2014,
    supports_recharge_rules_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_recharge_line_damage_2014 import (
    source_proven_recharge_line_damage_2014,
)

_scripts = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from browser_template_serializer import _save


def _behir():
    return next(item for item in load_monster_source_2014() if item.id == "behir")


def test_behir_source_compiles_exact_recharge_line_damage_parameters() -> None:
    source = _behir()
    binding = source_proven_recharge_line_damage_2014(source)[0]
    assert (binding.id, binding.name) == ("lightning-breath", "Lightning Breath")
    assert (binding.save_ability, binding.dc, binding.range_ft) == ("dexterity", 16, 20)
    assert binding.area.model_dump(exclude_none=True) == {
        "shape": "line", "origin": "self", "length_ft": 20, "width_ft": 5,
    }
    assert (binding.damage.count, binding.damage.size, binding.damage.bonus) == (12, 10, 0)
    assert binding.damage_type == "lightning" and binding.success_damage == "half"
    assert binding.resource_id == "lightning-breath" and binding.resource_cost == 1
    assert supports_recharge_rules_2014(source)
    assert [(item.id, item.max_uses) for item in save_resources_2014(source)] == [("lightning-breath", 1)]


def test_behir_binding_serializes_same_parameters_for_browser() -> None:
    card = next(item for item in save_capabilities_2014(_behir()) if item.id == "lightning-breath")
    browser = _save(_compile_save(card))
    assert browser["saveAbility"] == "dexterity" and browser["dc"] == 16
    assert browser["range"] == 20
    assert {key: value for key, value in browser["area"].items() if value is not None} == {
        "shape": "line", "origin": "self", "length_ft": 20, "width_ft": 5,
    }
    assert browser["damageDiceCount"] == 12 and browser["damageDiceSize"] == 10
    assert browser["damageType"] == "lightning" and browser["successDamage"] == "half"
    assert browser["resourceId"] == "lightning-breath"


def test_edited_or_incomplete_source_fails_closed_without_name_dispatch() -> None:
    source = _behir().model_copy(update={
        "id": "renamed-source",
        "name": "Renamed Source",
        "source_actions": _behir().source_actions.replace("20 feet long", "an unknown distance long"),
    })
    assert source_proven_recharge_line_damage_2014(source) == []
    assert not supports_recharge_rules_2014(source)


def test_renamed_card_with_unchanged_source_still_binds() -> None:
    source = _behir().model_copy(update={"id": "renamed-source", "name": "Renamed Source"})
    assert source_proven_recharge_line_damage_2014(source)[0].id == "lightning-breath"
