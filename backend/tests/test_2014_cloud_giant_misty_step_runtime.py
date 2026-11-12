"""Cloud Giant AI uses the shared Misty Step engine only for active holds."""
from __future__ import annotations

import logging

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple
from app.combat.state import begin_turn, build_combatant_state
from app.combat.teleport_policy import choose_teleport_action
from app.combat.teleport_resolution import resolve_teleport
from app.combat.timed_conditions import apply_timed_condition
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def test_cloud_giant_misty_step_only_clears_active_holds_without_moving():
    try:
        source = next(m for m in load_monster_source_2014() if m.id == "cloud-giant")
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        state = build_combatant_state(template)
        state.position = GridPosition(x=6, y=6)
        cloud = EncounterCombatant(
            combatant_id="cloud-giant", side="monsters", position_ft=30, state=state,
        )
        hero_state = build_combatant_state(build_goblin_warrior())
        hero_state.position = GridPosition(x=7, y=6)
        hero = EncounterCombatant(
            combatant_id="hero", side="heroes", position_ft=35, state=hero_state,
        )
        setup = EncounterSetup(
            heroes=[hero], monsters=[cloud], hero_total_levels=1,
            monster_total_cr="9", ruleset="2014",
            map_definition=build_standard_iron_pit_map(),
        )

        begin_turn(state)
        assert choose_teleport_action(cloud, setup, "1:cloud-giant") is None
        assert apply_timed_condition(
            state, "restrained", "hero", source_effect_id="entangle",
            source_is_magical=True, ground_contact=True, ends_on_teleport=True,
            use_default_poison_recovery=False,
        ) == "restrained"
        apply_grapple(state, "hero", 12, 5, restrains=True)
        resource = next(r for r in state.resources if r.id == "misty-step")
        resource.current_uses = 0
        assert choose_teleport_action(cloud, setup, "1:cloud-giant") is None
        resource.current_uses = 3
        choice = choose_teleport_action(cloud, setup, "1:cloud-giant")
        assert choice is not None
        action, destination = choice
        assert action.id == "misty-step"
        origin = state.position.model_copy(deep=True)
        assert destination == origin

        events, _ = resolve_teleport(
            1, 1, cloud, setup, action, destination,
            FixedDiceProvider([1]), "1:cloud-giant",
        )
        assert state.position == origin
        assert "restrained" not in state.active_effect_ids
        assert state.grapple_sources == []
        assert {"restrained", "grappled"} <= set(events[0].removed_condition_ids)
        assert next(r for r in state.resources if r.id == "misty-step").current_uses == 2
        assert state.bonus_action_available is False
    except Exception:
        logger.exception("Cloud Giant Misty Step in-place AI escape failed.")
        raise


def test_cloud_giant_misty_step_noop_resolution_spends_nothing():
    try:
        source = next(m for m in load_monster_source_2014() if m.id == "cloud-giant")
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        state = build_combatant_state(template)
        origin = GridPosition(x=6, y=6)
        state.position = origin
        cloud = EncounterCombatant(
            combatant_id="cloud-giant", side="monsters", position_ft=30, state=state,
        )
        hero_state = build_combatant_state(build_goblin_warrior())
        hero_state.position = GridPosition(x=7, y=6)
        hero = EncounterCombatant(
            combatant_id="hero", side="heroes", position_ft=35, state=hero_state,
        )
        setup = EncounterSetup(
            heroes=[hero], monsters=[cloud], hero_total_levels=1,
            monster_total_cr="9", ruleset="2014",
            map_definition=build_standard_iron_pit_map(),
        )
        begin_turn(state)
        action = template.teleport_actions[0]
        resource = next(r for r in state.resources if r.id == "misty-step")

        with pytest.raises(ValueError, match="no active teleport-cancelable effect"):
            resolve_teleport(
                1, 1, cloud, setup, action, origin,
                FixedDiceProvider([1]), "1:cloud-giant",
            )

        assert state.position == origin
        assert resource.current_uses == 3
        assert state.bonus_action_available is True
    except Exception:
        logger.exception("Cloud Giant Misty Step no-op guard failed.")
        raise
