"""Death Burst action fidelity across every structured 2014 source declaration."""
from app.combat.death_trigger_dispatch import _compile_death_save_action, _source_death_actions
from app.combat.death_trigger_rules import DEATH_TRIGGER_BUFF, consume_death_trigger
from app.combat.state import build_combatant_state
from app.content.roster import build_arena_roster


def test_all_structured_death_actions_use_shared_damage_saves():
    sources = _source_death_actions()
    assert sum(map(len, sources.values())) == 4
    for actions in sources.values():
        for raw in actions.values():
            action = _compile_death_save_action(raw)
            assert action.target_scope == "all-other-creatures"
            assert action.range_ft == raw["range_ft"]
            assert action.dc == raw["dc"]
            assert action.success_damage == raw["success_damage"]
            assert action.damage_type == raw["damage_type"]


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
