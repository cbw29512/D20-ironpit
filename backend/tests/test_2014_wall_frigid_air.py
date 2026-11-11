"""2014 source Wall of Ice: destroyed-section crossing uses normal save/damage."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.persistent_barrier_cast import cast_persistent_barrier
from app.combat.persistent_barrier_damage import apply_barrier_section_damage
from app.combat.persistent_barrier_frigid_air import resolve_destroyed_barrier_crossing
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_barriers import GridBarrierEdge

logger = logging.getLogger(__name__)


def _setup():
    try:
        source = next(row for row in load_monster_source_2014()
                      if row.id == "ice-devil")
        actor_state = build_combatant_state(
            compile_combatant(adapt_monster_mechanics_2014(source)),
        )
        actor_state.position = GridPosition(x=2, y=7)
        owner = EncounterCombatant(
            combatant_id="owner", side="monsters", position_ft=10, state=actor_state,
        )
        victim_state = build_combatant_state(build_goblin_warrior())
        victim_state.position = GridPosition(x=8, y=5)
        victim = EncounterCombatant(
            combatant_id="victim", side="heroes", position_ft=40, state=victim_state,
        )
        setup = EncounterSetup(
            heroes=[victim], monsters=[owner], ruleset="2014",
            hero_total_levels=1, monster_total_cr="14",
            map_definition=build_standard_iron_pit_map(),
        )
        panels = [
            [GridBarrierEdge(
                first=GridPosition(x=x, y=5),
                second=GridPosition(x=x, y=6),
            ) for x in range(start, start + 2)]
            for start in (6, 8)
        ]
        cast_persistent_barrier(
            1, 1, owner, setup,
            owner.state.template.persistent_barrier_actions[0], panels, "1:owner",
        )
        return source, owner, victim, setup
    except Exception:
        logger.exception("Could not arrange 2014 source wall crossing scenario.")
        raise


def test_destroyed_source_section_crossing_rolls_con_and_cold_damage():
    try:
        source, owner, victim, setup = _setup()
        unchanged = source.model_dump_json()
        barrier = setup.persistent_barriers[0]
        broken = barrier.sections[1]
        assert apply_barrier_section_damage(
            setup, barrier.barrier_id, broken.section_id, 30, "slashing",
        ).destroyed
        assert not barrier.sections[0].destroyed
        before_hp = victim.state.current_hp
        before = GridPosition(x=8, y=5)
        after = GridPosition(x=8, y=6)
        victim.state.position = after
        events, sequence = resolve_destroyed_barrier_crossing(
            2, 1, victim, setup, FixedDiceProvider([1, 1, 1, 1, 1, 1]),
            before, after, "1:victim",
        )
        saves = [event for event in events if event.event_type == "saving_throw"]
        assert len(saves) == 1
        assert (saves[0].feature_id, saves[0].save_dc) == ("wall-of-ice", 17)
        assert saves[0].save_ability == "constitution"
        assert not saves[0].save_succeeded
        assert victim.state.current_hp == before_hp - 5
        assert sequence > 2
        assert source.model_dump_json() == unchanged
    except Exception:
        logger.exception("2014 frigid-air save runtime regression failed.")
        raise


def test_air_expiry_and_intact_wall_do_not_create_extra_saves():
    try:
        _, owner, victim, setup = _setup()
        before = GridPosition(x=8, y=5)
        after = GridPosition(x=8, y=6)
        victim.state.position = after
        events, _ = resolve_destroyed_barrier_crossing(
            1, 1, victim, setup, FixedDiceProvider([20]),
            before, after, "1:victim",
        )
        assert events == []  # Intact wall; movement is stopped by pathing.
        barrier = setup.persistent_barriers[0]
        for section in barrier.sections:
            apply_barrier_section_damage(
                setup, barrier.barrier_id, section.section_id, 30, "slashing",
            )
        events, _ = resolve_destroyed_barrier_crossing(
            2, 1, victim, setup, FixedDiceProvider([20]),
            before, after, "1:victim",
        )
        assert events == []  # No remaining wall: air has dispersed.
        owner.state.is_unconscious = True
        assert not resolve_destroyed_barrier_crossing(
            3, 1, victim, setup, FixedDiceProvider([20]),
            before, after, "1:victim",
        )[0]
    except Exception:
        logger.exception("Generic destroyed-wall lifetime regression failed.")
        raise
