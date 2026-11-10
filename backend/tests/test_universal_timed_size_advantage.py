"""Temporary size, check Advantage and save Advantage share existing buff lifecycle."""
from __future__ import annotations

import logging

import pytest

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.size import CreatureSize
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def _action(action_id="growth", size=CreatureSize.LARGE):
    return TimedSelfBuffAction(
        id=action_id, name="Growth", action_cost="action",
        size_override=size, duration_rounds=10, expiry_timing="source_turn_start",
        ability_check_advantage_abilities=["strength"],
        saving_throw_advantage_grants=[SavingThrowAdvantageGrant(
            source_id="growth-save", source_name="Growth",
            abilities=["strength"],
        )],
    )


def _member():
    template = build_demo_fighter()
    state = build_combatant_state(template)
    return template, EncounterCombatant(
        combatant_id="source", side="heroes", position_ft=0, state=state,
    )


def test_generic_source_owned_size_and_strength_checks_are_fight_local():
    try:
        template, member = _member()
        original_size = template.size
        assert original_size == CreatureSize.MEDIUM
        event = resolve_timed_self_buff(
            1, 1, member, _action(), spend_action_cost=False,
        )
        state = member.state
        assert event.feature_id == "growth"
        assert template.size == original_size
        assert state.template.size == CreatureSize.LARGE
        assert state.timed_effects[0].expires_round == 11
        assert state.timed_effects[0].owned_previous_size == original_size
        assert ability_check_roll_mode(state, ability="strength").value == "advantage"
        assert ability_check_roll_mode(state, ability="dexterity").value == "normal"
        assert ability_check_roll_mode(state).value == "normal"
        strength, _ = resolve_saving_throw(
            state, "strength", 99, FixedDiceProvider([3, 16]),
        )
        assert strength.mode == "advantage" and strength.rolls == [3, 16]
        removed = remove_effect_group(state, state.timed_effects[0])
        assert removed == ["growth"]
        assert state.template.size == original_size
        assert template.size == original_size
        assert ability_check_roll_mode(state, ability="strength").value == "normal"
    except Exception:
        logger.exception("Generic temporary-size/check/save lifecycle regression")
        raise


def test_overlapping_size_override_fails_closed():
    try:
        _, member = _member()
        resolve_timed_self_buff(
            1, 1, member, _action(), spend_action_cost=False,
        )
        with pytest.raises(ValueError, match="already active"):
            resolve_timed_self_buff(
                2, 2, member, _action("other-growth", CreatureSize.HUGE),
                spend_action_cost=False,
            )
        assert member.state.template.size == CreatureSize.LARGE
    except Exception:
        logger.exception("Overlapping size ownership regression")
        raise
