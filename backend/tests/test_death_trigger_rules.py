"""Death Trigger is fight-local and fires on death, not the initial 0-HP drop."""
from app.combat.death_trigger_rules import DEATH_TRIGGER_BUFF, consume_death_trigger, death_trigger_ready
from app.combat.state import build_combatant_state
from app.content.roster import build_arena_roster


def test_character_zero_hp_is_not_death_trigger():
    cards = build_arena_roster()
    template = cards.characters[0]
    state = build_combatant_state(template)
    state.active_buff_effect_ids.append(DEATH_TRIGGER_BUFF)
    state.current_hp = 0
    state.is_unconscious = True
    assert not consume_death_trigger(state)
    state.death_save_failures = 3
    state.is_dead = True
    assert death_trigger_ready(state)
    assert consume_death_trigger(state)
    assert not consume_death_trigger(state)


def test_monster_zero_hp_death_trigger_once():
    cards = build_arena_roster()
    template = cards.monsters[0]
    state = build_combatant_state(template)
    state.active_buff_effect_ids.append(DEATH_TRIGGER_BUFF)
    state.current_hp = 0
    state.is_dead = True
    assert consume_death_trigger(state)
    assert not consume_death_trigger(state)
