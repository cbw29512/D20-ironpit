"""Real Chuul Pincer → Tentacles and grouped Poisoned/Paralyzed lifecycle."""
from __future__ import annotations

import logging

from app.combat.attack_actions import resolve_attack_action
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.saving_throw_legality import legal_save_action
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _fight():
    try:
        card = next(m for m in load_monster_source_2014() if m.id == "chuul")
        source = compile_combatant(adapt_monster_mechanics_2014(card))
        hero = build_demo_fighter().model_copy(update={"max_hp": 100})
        actor = EncounterCombatant(
            combatant_id="holder", side="monsters", position_ft=0,
            state=build_combatant_state(source),
        )
        victim = EncounterCombatant(
            combatant_id="hero", side="heroes", position_ft=5,
            state=build_combatant_state(hero),
        )
        setup = EncounterSetup(
            monsters=[actor], heroes=[victim], ruleset="2014",
            hero_total_levels=1, monster_total_cr="4",
        )
        action = next(a for a in source.saving_throw_actions if a.id == "tentacles")
        return actor, victim, setup, action
    except Exception:
        logger.exception("Could not construct source-backed Chuul fight")
        raise


def test_tentacles_fail_save_and_repeat_success_clear_both_conditions():
    try:
        actor, target, setup, action = _fight()
        assert not legal_save_action(
            action, target, 5, actor=actor, source_id=actor.combatant_id,
        )
        assert apply_grapple(target.state, actor.combatant_id, 14, 10, restrains=False)
        assert legal_save_action(
            action, target, 5, actor=actor, source_id=actor.combatant_id,
        )
        event = resolve_save_action(
            1, 1, actor, target, action, 5, FixedDiceProvider([1]),
            setup=setup,
        )
        assert event.save_succeeded is False
        assert event.feature_id == "tentacles"
        assert {"poisoned", "paralyzed"} <= set(target.state.active_effect_ids)
        effects = [e for e in target.state.timed_effects if e.source_effect_id == "tentacles"]
        assert len(effects) == 2
        lead = next(e for e in effects if e.effect_id == "poisoned")
        assert lead.expires_round == 11 and lead.repeat_save_timing == "target_turn_end"
        assert next(e for e in effects if e.effect_id == "paralyzed").repeat_save_timing is None
        # Print says the target repeats at the end of EACH following turn.
        saves, _ = resolve_target_condition_timing(
            2, 2, target, "target_turn_end", FixedDiceProvider([20]), setup,
        )
        assert len(saves) == 1 and saves[0].save_succeeded
        assert "poisoned" not in target.state.active_effect_ids
        assert "paralyzed" not in target.state.active_effect_ids
    except Exception:
        logger.exception("Chuul poison/paralysis grouped lifecycle failed")
        raise


def test_multiattack_adds_only_one_held_target_save_after_two_real_pincers():
    try:
        actor, target, setup, action = _fight()
        assert not target.state.grapple_sources
        # Two ordinary attack rolls and damage rolls, then the eligible save.
        events, _ = resolve_attack_action(
            1, 1, actor, setup, FixedDiceProvider([15, 3, 4, 15, 3, 4, 1]),
        )
        attacks = [e for e in events if e.event_type == "attack"]
        saves = [e for e in events if e.feature_id == action.id]
        assert len(attacks) == 2
        assert len(saves) == 1 and saves[0].save_succeeded is False
        assert target.state.current_hp < 100
        assert any(g.source_id == "holder" for g in target.state.grapple_sources)
        assert {"poisoned", "paralyzed"} <= set(target.state.active_effect_ids)
        assert actor.state.action_available is False
        # An unrelated grapple cannot authorize Tentacles.
        release_grapple(target.state, actor.combatant_id)
        assert not legal_save_action(
            action, target, 5, actor=actor, source_id=actor.combatant_id,
        )
    except Exception:
        logger.exception("Chuul live conditional Multiattack failed")
        raise
