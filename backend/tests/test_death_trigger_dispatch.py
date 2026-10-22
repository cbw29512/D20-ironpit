"""Death Trigger fidelity across every compatible 2014 source declaration."""
from app.combat.death_trigger_dispatch import _declared_actions
from app.combat.death_trigger_rules import DEATH_TRIGGER_BUFF, consume_death_trigger
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_death_triggers_2014 import (
    death_trigger_actions_2014,
    semantic_death_trigger_names_2014,
    supports_death_triggers_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.roster import build_arena_roster


def _source(monster_id):
    return next(card for card in load_monster_source_2014() if card.id == monster_id)


def test_all_compatible_death_actions_compile_to_shared_damage_saves():
    cards = load_monster_source_2014()
    structured = [card for card in cards if card.death_trigger_actions]
    compatible = [card for card in cards if death_trigger_actions_2014(card)]
    assert sum(len(card.death_trigger_actions) for card in structured) == 4
    assert [card.id for card in compatible] == [
        "balor", "dust-mephit", "ice-mephit", "magma-mephit", "magmin",
        "steam-mephit",
    ]
    for card in compatible:
        actions = death_trigger_actions_2014(card)
        assert actions and supports_death_triggers_2014(card)
        for action in actions:
            assert action.target_scope == "all-other-creatures"
            assert action.area.radius_ft == action.range_ft


def test_death_throes_uses_exact_immutable_source_parameters():
    source = _source("balor")
    action, = death_trigger_actions_2014(source)
    assert action.id == "death-throes" and action.name == "Death Throes"
    assert action.range_ft == 30 and action.dc == 20
    assert action.save_ability == "dexterity"
    assert (action.damage.count, action.damage.size, action.damage.bonus) == (20, 6, 0)
    assert action.damage_type.value == "fire" and action.success_damage == "half"
    assert source.death_trigger_actions == []


def test_source_proven_death_throes_survives_capability_compilation():
    actions = death_trigger_actions_2014(_source("balor"))
    definition = adapt_basic_monster_2014(_source("ape")).model_copy(update={
        "death_trigger_effect_ids": [action.id for action in actions],
        "death_trigger_actions": actions,
    })
    template = compile_combatant(definition)
    assert template.death_trigger_effect_ids == ["death-throes"]
    action, = template.death_trigger_actions
    assert action.id == "death-throes" and action.range_ft == 30
    state = build_combatant_state(template)
    assert DEATH_TRIGGER_BUFF in state.active_buff_effect_ids


def test_changed_death_throes_clause_fails_closed():
    source = _source("balor")
    mutant = source.model_copy(update={
        "source_traits": source.source_traits.replace(
            "or half as much damage on a successful one",
            "and no damage on a successful one",
        ),
    })
    assert semantic_death_trigger_names_2014(mutant) == ("Death Throes",)
    assert death_trigger_actions_2014(mutant) == []
    assert not supports_death_triggers_2014(mutant)


def test_condition_death_burst_uses_exact_immutable_source_parameters():
    source = _source("dust-mephit")
    action, = death_trigger_actions_2014(source)
    assert action.id == "death-burst" and action.name == "Death Burst"
    assert action.range_ft == 5 and action.dc == 10
    assert action.save_ability == "constitution" and action.damage is None
    rider = action.failed_save_timed_effect
    assert rider is not None and rider.effect_id == "blinded"
    assert rider.duration_rounds == 10 and rider.expiry_timing == "target_turn_end"
    assert (rider.repeat_save_ability, rider.repeat_save_dc) == ("constitution", 10)
    assert rider.repeat_save_timing == "target_turn_end"
    assert source.death_trigger_actions == []
    assert supports_death_triggers_2014(source)


def test_changed_death_burst_repeat_save_clause_fails_closed():
    source = _source("dust-mephit")
    mutant = source.model_copy(update={
        "source_traits": source.source_traits.replace(
            "on each of its turns", "at the end of each of its turns",
        ),
    })
    assert semantic_death_trigger_names_2014(mutant) == ("Death Burst",)
    assert death_trigger_actions_2014(mutant) == []
    assert not supports_death_triggers_2014(mutant)


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
