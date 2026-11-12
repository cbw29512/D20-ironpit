"""Shared next-target-turn Prone/end-turn behavior, independent of source name.

Source owns command timing, save and target eligibility; this test checks
generic effect execution and expiry, not full 2014 Command admission.
"""
from __future__ import annotations

import logging

import pytest

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.failed_save_timed_apply import apply_failed_save_timed_effect
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)


class NoRollDice:
    def roll(self, sides: int) -> int:
        raise AssertionError(f"Generic commanded turn unexpectedly rolled d{sides}.")


def member(name: str, side: str, pos: int) -> EncounterCombatant:
    try:
        template = build_karnok_stoneward().model_copy(deep=True)
        template.id = f"template-{name}"
        template.name = name
        return EncounterCombatant(
            combatant_id=name, side=side, position_ft=pos,
            state=build_combatant_state(template),
        )
    except Exception:
        logger.exception("Could not create generic timed-command fixture %s.", name)
        raise


@pytest.mark.parametrize("effect_name", ["Command", "Renamed Compulsion"])
def test_next_turn_prone_and_end_turn_preserves_normal_recovery(effect_name: str) -> None:
    try:
        source = member("caster", "monsters", 10)
        victim = member("victim", "heroes", 5)
        setup = EncounterSetup(
            heroes=[victim], monsters=[source],
            hero_total_levels=1, monster_total_cr="1",
        )
        rider = FailedSaveTimedEffect(
            effect_id="commanded",
            duration_target_turns=1,
            expiry_timing="target_turn_end",
            turn_behavior="fall_prone_end_turn",
        )
        action = SavingThrowAction(
            id=effect_name.lower().replace(" ", "-"), name=effect_name,
            save_ability="wisdom", dc=11, range_ft=60,
            failed_save_timed_effect=rider,
        )
        assert apply_failed_save_timed_effect(victim, source, action, 1, [
            source.state, victim.state,
        ], setup=setup) == "commanded"
        marker = victim.state.timed_effects[0]
        assert marker.expires_target_turn_count == 1
        assert marker.expires_round is None
        assert "prone" not in victim.state.active_effect_ids

        start_position = victim.position_ft
        events, _ = resolve_combat_turn(1, 1, victim, source, setup, NoRollDice())
        assert victim.position_ft == start_position
        assert victim.state.turn_terminated
        assert not victim.state.action_available
        assert not victim.state.bonus_action_available
        assert "prone" in victim.state.active_effect_ids
        event = next(e for e in events if e.feature_id == action.id)
        assert event.applied_condition_ids == ["prone"]
        assert "ends the turn" in event.description
        assert "flee" not in event.description.lower()
        assert not any(e.event_type in {"attack", "movement"} for e in events)

        end_events, _ = resolve_target_condition_timing(
            20, 1, victim, "target_turn_end", NoRollDice(),
        )
        assert victim.state.timed_effects == []
        assert "commanded" not in victim.state.active_effect_ids
        assert "prone" in victim.state.active_effect_ids
        assert any(e.removed_condition_ids == ["commanded"] for e in end_events)
        begin_turn(victim.state)
        assert "prone" not in victim.state.active_effect_ids
    except Exception:
        logger.exception("Generic target-turn Prone/end-turn regression failed.")
        raise


def test_target_turn_expiry_validates_source_schema() -> None:
    try:
        with pytest.raises(ValueError, match="target-turn duration"):
            FailedSaveTimedEffect(
                effect_id="commanded", duration_target_turns=1,
                duration_rounds=1, turn_behavior="fall_prone_end_turn",
            )
        with pytest.raises(ValueError, match="exact target-turn duration"):
            FailedSaveTimedEffect(
                effect_id="commanded", turn_behavior="fall_prone_end_turn",
            )
    except Exception:
        logger.exception("Generic target-turn expiry validation regressed.")
        raise
