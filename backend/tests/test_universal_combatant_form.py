"""Contract tests: a submitted homebrew form uses the official combat pipeline."""
from __future__ import annotations

import copy

import pytest

from app.content.combatant_form import compile_combatant_form
from app.content.capability_compiler import compile_combatant
from app.combat.state import build_combatant_state
from app.domain.capabilities import CombatantDefinition


def form(name: str = "Original") -> dict:
    return {
        "schema_version": 1, "id": "form-fighter", "name": name,
        "archetype": "custom", "kind": "monster", "ruleset": "2014",
        "armor_class": 14, "max_hp": 31, "speed_ft": 30,
        "initiative_bonus": 2,
        "attacks": [{
            "id": "tail", "name": "Burning Coil" if name != "Original" else "Tail",
            "attack_kind": "melee", "attack_bonus": 5,
            "damage": {"count": 2, "size": 6, "bonus": 3},
            "damage_type": "bludgeoning", "animation": "slash",
            "effects": [{"kind": "damage", "source": "heated",
                         "dice": {"count": 1, "size": 6}, "damage_type": "fire"}],
        }],
        "primary_attack_id": "tail",
        "visual": {"armor": "natural", "main_hand": "tail", "body_style": "beast"},
        "source": "user-created test form",
    }


def test_homebrew_form_compiles_through_same_template_as_official_definition() -> None:
    original = form()
    normal = compile_combatant(CombatantDefinition.model_validate(original))
    custom = compile_combatant_form(copy.deepcopy(original))
    assert custom.model_dump() == normal.model_dump()
    state = build_combatant_state(custom)
    assert state.current_hp == 31
    assert custom.max_hp == 31


def test_ability_names_are_labels_not_resolution_switches() -> None:
    original_payload = form()
    renamed_payload = copy.deepcopy(original_payload)
    renamed_payload["attacks"][0]["name"] = "Completely Different Label"
    original = compile_combatant_form(original_payload)
    renamed = compile_combatant_form(renamed_payload)
    assert original.weapon_attack.attack_bonus == renamed.weapon_attack.attack_bonus
    assert original.weapon_attack.on_hit_damage == renamed.weapon_attack.on_hit_damage
    assert renamed.weapon_attack.weapon.name == "Completely Different Label"
    assert original.weapon_attack.weapon.name == "Tail"


def test_form_rejects_silent_unknown_effect_fields() -> None:
    payload = form()
    payload["my_secret_mechanic"] = {"kind": "paralyze"}
    with pytest.raises(ValueError, match="combatant has unknown fields"):
        compile_combatant_form(payload)


def test_form_rejects_invalid_attack_references() -> None:
    payload = form()
    payload["primary_attack_id"] = "missing"
    with pytest.raises(ValueError, match="primary_attack_id"):
        compile_combatant_form(payload)


def test_form_fails_closed_for_unsupported_mechanics() -> None:
    payload = form()
    payload["unsupported_capabilities"] = ["unimplemented:custom-effect"]
    with pytest.raises(ValueError, match="unsupported capabilities"):
        compile_combatant_form(payload)


@pytest.mark.parametrize("location", ["attack", "effect", "dice", "save"])
def test_nested_unknown_mechanic_fails_closed(location: str) -> None:
    payload = form()
    if location == "attack":
        payload["attacks"][0]["secret_trigger"] = "on_hit"
    elif location == "effect":
        payload["attacks"][0]["effects"][0]["secret_condition"] = "paralyzed"
    elif location == "dice":
        payload["attacks"][0]["damage"]["bonus_damage_type"] = "fire"
    else:
        payload["save_actions"] = [{
            "id": "shriek", "name": "Arbitrary Label", "save_ability": "wisdom",
            "dc": 15, "range_ft": 15, "hidden_success_effect": "frightened",
        }]
    with pytest.raises(ValueError, match="unknown fields"):
        compile_combatant_form(payload)


def test_hit_modifier_unknown_payload_is_rejected() -> None:
    payload = form()
    payload["attacks"][0]["effects"].append({
        "kind": "speed", "flat_bonus": -10,
        "unexpected_duration": 3,
    })
    with pytest.raises(ValueError, match="unknown fields"):
        compile_combatant_form(payload)


@pytest.mark.parametrize("nested", ["charge", "charge_damage", "save_damage", "save_grapple"])
def test_additional_nested_form_values_fail_closed(nested: str) -> None:
    payload = form()
    if nested in {"charge", "charge_damage"}:
        charge = {"minimum_move_ft": 10, "bonus_damage": {
            "dice_count": 2, "dice_size": 6, "damage_type": "bludgeoning",
        }}
        if nested == "charge":
            charge["invented_trigger"] = True
        else:
            charge["bonus_damage"]["invented_multiplier"] = 3
        payload["attacks"][0]["charge_profile"] = charge
    else:
        action = {"id": "blast", "name": "Arbitrary Label",
                  "save_ability": "wisdom", "dc": 15, "range_ft": 15}
        if nested == "save_damage":
            action.update(damage={"count": 2, "size": 6, "invented_rider": 9},
                          damage_type="fire")
        else:
            action["grapple"] = {"escape_dc": 15, "invented_grapple_rule": True}
        payload["save_actions"] = [action]
    with pytest.raises(ValueError, match="unknown fields"):
        compile_combatant_form(payload)
