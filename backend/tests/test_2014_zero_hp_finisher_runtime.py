"""A printed zero-HP Bonus Action uses the universal save/death/healing engine."""
from __future__ import annotations

import logging

import pytest

from app.combat.bonus_save_actions import choose_bonus_save_action
from app.combat.encounter_turn_support import finish_turn
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_legality import legal_save_action
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _encounter():
    try:
        source = next(m for m in load_monster_source_2014() if m.id == "will-o-wisp")
        template = compile_combatant(adapt_basic_monster_2014(source))
        wisp = EncounterCombatant(
            combatant_id="wisp", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        wisp.state.current_hp = 8
        victim = EncounterCombatant(
            combatant_id="victim", side="heroes", position_ft=5,
            state=build_combatant_state(build_commoner().model_copy(update={"ruleset": "2014", "kind": "character"})),
        )
        victim.state.current_hp = 0
        victim.state.is_alive = True
        victim.state.is_dead = False
        victim.state.is_unconscious = True
        setup = EncounterSetup(
            heroes=[victim], monsters=[wisp], hero_total_levels=1,
            monster_total_cr="2", ruleset="2014",
        )
        action = next(a for a in wisp.state.template.saving_throw_actions if a.id == "consume-life")
        assert action.range_ft == 5
        invis = next(a for a in wisp.state.template.timed_self_buff_actions if a.id == "invisibility")
        return wisp, victim, setup, action, invis
    except Exception:
        logger.exception("Could not create source-backed 2014 finisher encounter.")
        raise


def test_failed_save_kills_and_heals_only_after_terminal_death():
    try:
        actor, victim, setup, action, invis = _encounter()
        states = [actor.state, victim.state]
        resolve_timed_self_buff(1, 1, actor, invis, spend_action_cost=False, affected_states=states)
        assert "invisible" in actor.state.active_effect_ids and actor.state.concentration
        chosen = choose_bonus_save_action(actor, setup)
        assert chosen is not None and chosen[0].id == "consume-life"
        assert chosen[2].combatant_id == victim.combatant_id
        event = resolve_save_action(
            2, 1, actor, victim, action, 5,
            FixedDiceProvider([1, 2, 3, 4]), affected_states=states, setup=setup,
        )
        assert event.feature_id == "consume-life" and event.save_succeeded is False
        assert victim.state.is_dead and not victim.state.is_alive
        assert event.is_dead is True
        assert event.healing_roll is not None
        assert event.healing_roll.total == 9 and actor.state.current_hp == 17
        assert actor.state.bonus_action_available is False
        assert "invisible" not in actor.state.active_effect_ids
        assert actor.state.concentration is None
        assert "Consume Life" in event.description
    except Exception:
        logger.exception("Zero-HP failed-save death/healing regression failed.")
        raise


def test_successful_save_causes_no_death_or_healing_but_breaks_invisibility():
    try:
        actor, victim, setup, action, invis = _encounter()
        states = [actor.state, victim.state]
        resolve_timed_self_buff(1, 1, actor, invis, spend_action_cost=False, affected_states=states)
        result = resolve_save_action(
            2, 1, actor, victim, action, 5,
            FixedDiceProvider([20]), affected_states=states, setup=setup,
        )
        assert result.save_succeeded
        assert result.healing_roll is None
        assert actor.state.current_hp == 8
        assert victim.state.is_alive and victim.state.current_hp == 0 and not victim.state.is_dead
        assert actor.state.concentration is None
        assert "invisible" not in actor.state.active_effect_ids
    except Exception:
        logger.exception("Successful finisher save incorrectly changed HP or Invisible.")
        raise


def test_dead_or_positive_hp_target_never_qualifies():
    try:
        actor, victim, setup, action, _ = _encounter()
        victim.state.current_hp = 2
        assert not legal_save_action(action, victim, 5, actor=actor, source_id=actor.combatant_id)
        assert choose_bonus_save_action(actor, setup) is None
        victim.state.current_hp = 0
        victim.state.is_dead = True
        victim.state.is_alive = False
        assert not legal_save_action(action, victim, 5, actor=actor, source_id=actor.combatant_id)
        assert choose_bonus_save_action(actor, setup) is None
        victim.state.is_dead = False
        victim.state.is_alive = True
        assert legal_save_action(action, victim, 5, actor=actor, source_id=actor.combatant_id)
        assert not legal_save_action(action, victim, 10, actor=actor, source_id=actor.combatant_id)
        with pytest.raises(ValueError):
            resolve_save_action(1, 1, actor, victim, action, 10, FixedDiceProvider([1]), setup=setup)
    except Exception:
        logger.exception("Zero-HP finisher target legality failed.")
        raise


def test_post_action_bonus_save_uses_newly_downed_target():
    try:
        actor, victim, setup, action, _ = _encounter()
        victim.state.current_hp = 1
        assert choose_bonus_save_action(actor, setup) is None
        # Simulate the immediately preceding ordinary Attack Action.
        actor.state.action_available = False
        victim.state.current_hp = 0
        events, next_sequence = finish_turn(
            [], 2, 1, actor, setup, FixedDiceProvider([1, 2, 3, 4]),
            "1:wisp", allow_surge=False,
        )
        consumed = [event for event in events if event.feature_id == action.id]
        assert len(consumed) == 1 and next_sequence > 2
        assert consumed[0].save_succeeded is False
        assert consumed[0].healing_roll.total == 9
        assert victim.state.is_dead
        assert actor.state.current_hp == 17
        assert actor.state.bonus_action_available is False
    except Exception:
        logger.exception("Post-action generic Bonus Action finisher did not resolve.")
        raise
