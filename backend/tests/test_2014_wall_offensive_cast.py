"""Real 2014 source wall selects a normal Action and applies printed Cold save."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.persistent_barrier_offense import choose_offensive_barrier
from app.combat.persistent_barrier_offense_resolution import resolve_offensive_barrier
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def _member(template, identifier, side, x, y):
    try:
        state = build_combatant_state(template)
        state.position = GridPosition(x=x, y=y)
        return EncounterCombatant(
            combatant_id=identifier, side=side, position_ft=x * 5, state=state,
        )
    except Exception:
        logger.exception("Could not create source-neutral barrier test combatant.")
        raise


def _setup(*, target_x=8, target_y=5):
    try:
        source = next(row for row in load_monster_source_2014()
                      if row.id == "ice-devil")
        caster = _member(
            compile_combatant(adapt_monster_mechanics_2014(source)),
            "wall-owner", "monsters", 2, 7,
        )
        victim = _member(
            build_goblin_warrior(), "victim", "heroes", target_x, target_y,
        )
        setup = EncounterSetup(
            heroes=[victim], monsters=[caster], ruleset="2014",
            hero_total_levels=1, monster_total_cr="14",
            map_definition=build_standard_iron_pit_map(),
        )
        return source, caster, victim, setup
    except Exception:
        logger.exception("Could not build real 2014 wall fight.")
        raise


def test_offensive_wall_uses_existing_save_and_resource_event_chain():
    try:
        source, owner, victim, setup = _setup()
        unchanged = source.model_dump_json()
        choice = choose_offensive_barrier(owner, setup)
        assert choice is not None
        assert choice.action.name == "Wall of Ice"
        assert victim.combatant_id in choice.affected_ids
        assert choice.expected_damage >= 35
        before = victim.state.current_hp
        events, sequence = resolve_offensive_barrier(
            1, 1, owner, setup, FixedDiceProvider([1, *([1] * 10)]),
            "1:wall-owner", choice,
        )
        assert sequence > 2
        assert events[0].event_type == "feature"
        assert events[0].feature_id == "wall-of-ice"
        saves = [event for event in events if event.event_type == "saving_throw"]
        assert len(saves) == 1
        assert saves[0].save_dc == 17 and not saves[0].save_succeeded
        assert saves[0].save_ability == "dexterity"
        assert victim.state.current_hp < before
        assert any(resource.id == "wall-of-ice" and resource.current_uses == 0
                   for resource in owner.state.resources)
        assert setup.persistent_barriers[0].sections[0].current_hp == 30
        assert choose_offensive_barrier(owner, setup) is None
        assert source.model_dump_json() == unchanged
    except Exception:
        logger.exception("Printed 2014 wall Action/damage regression failed.")
        raise


def test_offensive_barrier_boundary_and_empty_resource_fail_closed():
    try:
        _, owner, victim, setup = _setup(target_x=23, target_y=15)
        assert choose_offensive_barrier(owner, setup) is not None
        resource = next(r for r in owner.state.resources if r.id == "wall-of-ice")
        resource.current_uses = 0
        assert choose_offensive_barrier(owner, setup) is None
        # Creatures without a sourced damaging wall never gain this Action.
        assert not victim.state.template.persistent_barrier_actions
        assert choose_offensive_barrier(victim, setup) is None
    except Exception:
        logger.exception("Generic barrier boundary/resource regression failed.")
        raise
