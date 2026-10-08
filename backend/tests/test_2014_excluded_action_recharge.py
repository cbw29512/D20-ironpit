from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_arena_action_policy_2014 import arena_unavailable_recharge_ids_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_save_capabilities_2014 import (
    recharge_rules_2014,
    supports_recharge_rules_2014,
    unsupported_source_actions_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row


def _blink_dog():
    return next(monster for monster in load_monster_source_2014() if monster.id == "blink-dog")


def test_blink_dog_printed_teleport_recharge_has_no_arena_resource_or_bonus_bite() -> None:
    monster = _blink_dog()
    assert monster.action_recharges == {"teleport": 4}
    assert "Teleport (Recharge 4" in monster.source_actions
    assert monster.action_names == ["Bite", "Teleport (Recharge 4–6)"]
    assert arena_unavailable_recharge_ids_2014(monster) == frozenset({"teleport"})
    assert supports_recharge_rules_2014(monster)
    assert recharge_rules_2014(monster) == []
    assert basic_blockers_2014(monster) == ()

    definition = adapt_basic_monster_2014(monster)
    assert definition.ruleset == "2014"
    assert len(definition.attacks) == 1
    assert definition.attacks[0].name == "Bite"
    assert not definition.attack_action
    assert definition.resources == []
    assert definition.recharge_rules == []
    template = compile_combatant(definition)
    browser = template_row(template)
    assert [(action["name"], action["diceCount"], action["diceSize"]) for action in browser["attacks"]] == [
        ("Bite", 1, 6),
    ]
    assert browser["resources"] == {}
    assert browser.get("recharge_rules", []) == []


def test_unknown_or_unprinted_recharge_remains_fail_closed() -> None:
    monster = _blink_dog()
    altered = monster.model_copy(update={"action_recharges": {"unknown-effect": 4}})
    assert not supports_recharge_rules_2014(altered)
    assert "mechanic:recharge" in basic_blockers_2014(altered)

    unprinted = monster.model_copy(update={"action_names": ["Bite"]})
    assert not arena_unavailable_recharge_ids_2014(unprinted)
    assert not supports_recharge_rules_2014(unprinted)
    assert "mechanic:recharge" in basic_blockers_2014(unprinted)


def test_printed_excluded_teleport_does_not_hide_other_recharge_mechanics() -> None:
    monster = _blink_dog()
    mixed = monster.model_copy(update={"action_recharges": {"teleport": 4, "unknown-effect": 5}})
    assert arena_unavailable_recharge_ids_2014(mixed) == frozenset({"teleport"})
    assert not supports_recharge_rules_2014(mixed)
    assert recharge_rules_2014(mixed) == []
    assert "mechanic:recharge" in basic_blockers_2014(mixed)
    assert "Teleport (Recharge 4–6)" in unsupported_source_actions_2014(monster)
