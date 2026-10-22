from __future__ import annotations

import pytest

from scripts.compile_custom_monster_card import compile_custom_monster


def source_card():
    return {
        "schema_version": 1, "id": "test-dummy-zero-ac", "name": "Test Dummy",
        "archetype": "test", "kind": "monster", "ruleset": "2014",
        "armor_class": 0, "max_hp": 16, "speed_ft": 0, "initiative_bonus": 0,
        "attacks": [{
            "id": "tap", "name": "Tap", "attack_kind": "melee",
            "attack_bonus": 2, "damage": {"count": 1, "size": 4, "bonus": 0},
            "damage_type": "bludgeoning", "animation": "slash",
            "effects": [{
                "kind": "damage", "source": "heated",
                "dice": {"count": 1, "size": 6, "bonus": 0}, "damage_type": "fire",
            }],
        }],
        "primary_attack_id": "tap", "source": "homebrew test",
    }


def test_custom_monster_exports_actual_browser_template_and_preserves_ac_zero():
    browser = compile_custom_monster(source_card())
    assert isinstance(browser, dict)
    assert browser["id"] == "test-dummy-zero-ac"
    assert browser["ruleset"] == "2014"
    assert browser["armor_class"] == 0


def test_homebrew_rejects_pregen_until_raw_leveling_is_available():
    payload = source_card()
    payload["kind"] = "character"
    with pytest.raises(ValueError, match="RAW progression"):
        compile_custom_monster(payload)


def test_source_form_rejects_library_flags_and_unknown_mechanics():
    payload = source_card()
    payload["custom"] = True
    with pytest.raises(ValueError, match="metadata"):
        compile_custom_monster(payload)
    payload = source_card()
    payload["unimplemented_attack"] = {"damage": "100d100"}
    with pytest.raises(ValueError, match="unknown fields"):
        compile_custom_monster(payload)
