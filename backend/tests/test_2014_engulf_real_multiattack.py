"""Real 2014 Multiattack resolution must trigger the same Engulf engine."""
from __future__ import annotations

import logging
from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _combat():
    source = next(m for m in load_monster_source_2014() if m.id == "shambling-mound")
    monster = compile_combatant(adapt_monster_mechanics_2014(source))
    hero = build_demo_fighter().model_copy(update={"max_hp": 100})
    attacker = EncounterCombatant(
        combatant_id="mound", side="monsters", position_ft=0,
        state=build_combatant_state(monster),
    )
    defender = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=5,
        state=build_combatant_state(hero),
    )
    setup = EncounterSetup(
        heroes=[defender], monsters=[attacker], hero_total_levels=1,
        monster_total_cr="5", ruleset="2014",
    )
    return attacker, defender, setup


def test_two_real_slams_trigger_one_printed_engulf():
    try:
        actor, target, setup = _combat()
        assert actor.state.template.attack_action is not None
        assert len(actor.state.template.attack_action.slots) == 2
        events, sequence = resolve_attack_action(
            1, 1, actor, setup, FixedDiceProvider([15, 4, 4, 15, 4, 4]),
        )
        attacks = [e for e in events if e.event_type == "attack"]
        linked = [e for e in events if e.feature_id == "Engulf"]
        assert len(attacks) == 2 and all(e.hit for e in attacks)
        assert len(linked) == 1 and linked[0].target_id == "hero"
        assert sequence == 4
        assert target.state.grapple_sources[0].linked_effect_id == "engulf"
        assert target.state.grapple_sources[0].escape_dc == 14
        assert "blinded" in target.state.active_effect_ids
        assert "restrained" in target.state.active_effect_ids
    except Exception:
        logger.exception("Real two-Slam Engulf combat regression failed")
        raise


def test_missed_second_slam_never_triggers_engulf():
    try:
        actor, target, setup = _combat()
        events, _ = resolve_attack_action(
            1, 1, actor, setup, FixedDiceProvider([15, 4, 4, 1]),
        )
        attacks = [e for e in events if e.event_type == "attack"]
        assert len(attacks) == 2 and attacks[0].hit and not attacks[1].hit
        assert not any(e.feature_id == "Engulf" for e in events)
        assert target.state.grapple_sources == []
    except Exception:
        logger.exception("Missed second Slam incorrectly applied Engulf")
        raise
