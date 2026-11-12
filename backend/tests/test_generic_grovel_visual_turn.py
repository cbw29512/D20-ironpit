"""A delayed generic command cannot suppress involuntary visual start effects.

Immutable source: a printed Sea Hag visual rule and renamed generic command.
Fight-local state: gaze condition plus next-target-turn command marker, then Prone.
"""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.failed_save_timed_apply import apply_failed_save_timed_effect
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)


def test_involuntary_gaze_runs_before_delayed_grovel_without_voluntary_actions() -> None:
    try:
        # Real source rule: a failed Sea Hag visual save applies Frightened.
        sources = {row.id: row for row in load_monster_source_2014()}
        rule = visual_turn_start_rule_2014(sources["sea-hag"])
        assert rule is not None
        template = compile_combatant(adapt_basic_monster_2014(sources["commoner"]))
        source = EncounterCombatant(
            combatant_id="source", side="monsters", position_ft=10,
            state=build_combatant_state(
                template.model_copy(update={"visual_turn_start_rule": rule})
            ),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=0,
            state=build_combatant_state(template),
        )
        setup = EncounterSetup(
            heroes=[target], monsters=[source], ruleset="2014",
            hero_total_levels=0, monster_total_cr="0",
        )
        action = SavingThrowAction(
            id="renamed-command", name="Renamed Command",
            save_ability="wisdom", dc=11, range_ft=60,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="commanded", duration_target_turns=1,
                expiry_timing="target_turn_end",
                turn_behavior="fall_prone_end_turn",
            ),
        )
        assert apply_failed_save_timed_effect(
            target, source, action, 1, [source.state, target.state], setup=setup,
        ) == "commanded"

        events, _ = resolve_combat_turn(
            1, 1, target, source, setup,
            FixedDiceProvider([1] * 16), initiative_order=["source", "target"],
        )
        gaze = [event for event in events if event.feature_id == rule.source_id]
        compelled = [event for event in events if event.feature_id == action.id]
        assert len(gaze) == len(compelled) == 1
        assert gaze[0].sequence < compelled[0].sequence
        assert gaze[0].applied_condition_ids == ["frightened"]
        assert "frightened" in target.state.active_effect_ids
        assert "prone" in target.state.active_effect_ids
        assert target.state.turn_terminated
        assert not target.state.action_available
        assert not target.state.bonus_action_available
        assert target.position_ft == 0
        assert not any(event.event_type in {"attack", "movement"} for event in events)
    except Exception:
        logger.exception("Mandatory visual turn-start effects were skipped by a command.")
        raise
