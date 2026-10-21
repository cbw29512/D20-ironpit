"""Death Trigger action fidelity across every compatible 2014 source declaration."""
from app.combat.death_trigger_dispatch import _declared_actions
from app.combat.death_trigger_rules import DEATH_TRIGGER_BUFF, consume_death_trigger
from app.combat.state import build_combatant_state
from app.content.monster_death_triggers_2014 import death_trigger_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.roster import build_arena_roster


def test_all_structured_death_actions_compile_to_shared_damage_saves():
    cards = [card for card in load_monster_source_2014() if card.death_trigger_actions]
    assert sum(len(card.death_trigger_actions) for card in cards) == 4
    for card in cards:
        actions = death_trigger_actions_2014(card)
        assert len(actions) == len(card.death_trigger_actions)
        for action, raw in zip(actions, card.death_trigger_actions, strict=True):
            assert action.target_scope == "all-other-creatures"
            assert action.range_ft == raw["range_ft"]
            assert action.dc == raw["dc"]
            assert action.success_damage == raw["success_damage"]
            assert action.damage_type.value == raw["damage_type"]


def test_declared_effect_ids_fail_closed_when_payload_is_missing():
    card = build_arena_roster().monsters[0]
    state = build_combatant_state(card.model_copy(update={
        "death_trigger_effect_ids": ["missing"], "death_trigger_actions": [],
    }))
    source = type("Member", (), {"state": state})()
    try:
        _declared_actions(source)
    except ValueError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Missing Death Trigger payload must fail closed.")


def test_death_trigger_never_fires_at_hero_zero_hp():
    card = build_arena_roster().characters[0]
    template = card.model_copy(update={"death_trigger_effect_ids": ["death-burst"]})
    hero = build_combatant_state(template)
    assert DEATH_TRIGGER_BUFF in hero.active_buff_effect_ids
    hero.current_hp = 0
    hero.is_unconscious = True
    assert consume_death_trigger(hero) is False
    hero.death_save_failures = 3
    hero.is_dead = True
    assert consume_death_trigger(hero) is True
    assert consume_death_trigger(hero) is False
