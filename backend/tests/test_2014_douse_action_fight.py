"""Recurring fire may be doused by the shared Action economy and timed effect engine."""
from __future__ import annotations

import logging

import pytest

from app.combat.action_economy import is_available
from app.combat.douse_burning import choose_douse_target, douseable_effects, resolve_douse_action
from app.combat.encounter_turn_support import resolve_support_actions
from app.combat.state import build_combatant_state
from app.combat.end_of_turn_recurring_damage import resolve_end_turn_recurring_damage
from app.combat.dice import FixedDiceProvider
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def _scene():
    try:
        template = build_demo_fighter()
        def member(identifier, side):
            return EncounterCombatant(
                combatant_id=identifier, side=side, position_ft=5,
                state=build_combatant_state(template),
            )
        burned = member("burned", "heroes")
        helper = member("helper", "heroes")
        enemy = member("enemy", "monsters")
        scene = EncounterSetup(
            heroes=[burned, helper], monsters=[enemy], ruleset="2014",
            hero_total_levels=2, monster_total_cr="1",
        )
        burned.state.timed_effects.append(TimedEffect(
            effect_id="burning", source_id="enemy", source_effect_id="attack-1",
            source_name="Printed Contact Attack", end_of_turn_dice_count=1,
            end_of_turn_dice_size=6, end_of_turn_damage_type="fire",
            ends_if_source_dead=False, expires_at_start_of_source_turn=False,
            allowed_removal_action_ids=["douse-fire"],
        ))
        burned.state.active_effect_ids.append("burning")
        return burned, helper, enemy, scene
    except Exception:
        logger.exception("Douse regression scene setup failed")
        raise


def test_self_douse_uses_action_and_prevents_turn_end_damage():
    try:
        burned, helper, _, scene = _scene()
        assert choose_douse_target(burned, scene) is burned
        before = burned.state.current_hp
        event = resolve_douse_action(5, 2, burned, burned)
        assert event.feature_id == "douse-fire"
        assert "Printed Contact Attack" in event.description
        assert "burning" not in burned.state.active_effect_ids
        assert not burned.state.timed_effects
        assert not is_available(burned.state, "action")
        after, sequence = resolve_end_turn_recurring_damage(
            6, 2, burned, scene, FixedDiceProvider([4]),
        )
        assert after == [] and sequence == 6 and burned.state.current_hp == before
        with pytest.raises(ValueError, match="Target has no"):
            resolve_douse_action(7, 2, helper, burned)
    except Exception:
        logger.exception("Self-douse turn lifecycle failed")
        raise


def test_self_douse_is_wired_into_ordinary_turn_support():
    try:
        burned, helper, _, scene = _scene()
        assert choose_douse_target(burned, scene) is burned
        more, sequence = resolve_support_actions(
            1, 1, burned, scene, FixedDiceProvider([10]), "1:burned",
        )
        assert sequence > 1
        assert any(event.feature_id == "douse-fire" for event in more)
        assert burned.state.timed_effects == []
        assert not burned.state.action_available
    except Exception:
        logger.exception("Self-douse support integration failed")
        raise


def test_no_douse_permission_or_no_action_fails_closed():
    try:
        burned, helper, _, scene = _scene()
        burned.state.timed_effects[0].allowed_removal_action_ids = []
        assert douseable_effects(burned) == []
        assert choose_douse_target(helper, scene) is None
        with pytest.raises(ValueError, match="Helper dousing"):
            resolve_douse_action(1, 1, helper, burned)
        assert helper.state.action_available
        burned.state.timed_effects[0].allowed_removal_action_ids = ["douse-fire"]
        helper.state.action_available = False
        assert choose_douse_target(burned, scene) is burned
        burned.state.action_available = False
        assert choose_douse_target(burned, scene) is None
        with pytest.raises(ValueError, match="available Action"):
            resolve_douse_action(1, 1, burned, burned)
    except Exception:
        logger.exception("Douse source authorization/economy guard failed")
        raise
