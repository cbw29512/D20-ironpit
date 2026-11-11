"""Generic Recharge/owner-expiry support for destructible source barriers."""
from __future__ import annotations

import logging

import pytest

from app.combat.persistent_barrier_cast import cast_persistent_barrier
from app.combat.persistent_barrier_lifecycle import cleanup_persistent_barriers
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_barriers import GridBarrierEdge
from scripts.browser_template_serializer import persistent_barrier_row

logger = logging.getLogger(__name__)


def _member(template, identifier, side, x, y):
    try:
        state = build_combatant_state(template)
        state.position = GridPosition(x=x, y=y)
        return EncounterCombatant(
            combatant_id=identifier, side=side, position_ft=x * 5, state=state,
        )
    except Exception:
        logger.exception("Failed to prepare barrier combatant.")
        raise


def _cast():
    try:
        owner = _member(build_thalen_greenbough_level(9), "owner", "heroes", 2, 7)
        target = _member(build_goblin_warrior(), "target", "monsters", 20, 7)
        setup = EncounterSetup(
            heroes=[owner], monsters=[target], hero_total_levels=9,
            monster_total_cr="1/4", ruleset="2024",
            map_definition=build_standard_iron_pit_map(),
        )
        spell = owner.state.template.persistent_barrier_actions[0]
        # This is a generic non-spell Action configured from source fields.
        action = spell.model_copy(update={
            "level": 0, "concentration": False,
            "permanent_after_full_duration": False,
            "resource_id": "spell-slot-5", "resource_cost": 1,
            "ends_on_source_incapacitated": True,
            "ends_on_source_death": True,
        })
        panels = [
            [
                GridBarrierEdge(
                    first=GridPosition(x=x, y=4),
                    second=GridPosition(x=x, y=5),
                ),
                GridBarrierEdge(
                    first=GridPosition(x=x + 1, y=4),
                    second=GridPosition(x=x + 1, y=5),
                ),
            ]
            for x in range(2, 22, 2)
        ]
        event, _ = cast_persistent_barrier(
            1, 1, owner, setup, action, panels, "1:owner",
        )
        return setup, owner, event, action, spell, panels
    except Exception:
        logger.exception("Generic non-spell barrier cast failed.")
        raise


def test_resource_owned_barrier_spends_and_preserves_source() -> None:
    try:
        setup, owner, event, action, spell, panels = _cast()
        slot = next(r for r in owner.state.resources if r.id == "spell-slot-5")
        assert event.resource_remaining == 0
        assert slot.current_uses == 0
        assert owner.state.concentration is None
        assert spell.resource_id is None
        assert spell.ends_on_source_incapacitated is False
        row = persistent_barrier_row(action)
        assert row["resourceId"] == "spell-slot-5"
        assert row["resourceCost"] == 1
        assert row["endsOnSourceIncapacitated"]
        assert row["endsOnSourceDeath"]
        assert "resourceId" not in persistent_barrier_row(spell)
        wall = setup.persistent_barriers[0]
        assert wall.ends_on_source_incapacitated is True
        assert wall.ends_on_source_death is True
        owner.state.action_available = True
        with pytest.raises(ValueError, match="resource remains"):
            cast_persistent_barrier(
                2, 2, owner, setup, action, panels, "2:owner",
            )
        assert len(setup.persistent_barriers) == 1
    except Exception:
        logger.exception("Resource ownership regression failed.")
        raise


@pytest.mark.parametrize("ending", ["incapacitated", "dead", "expired"])
def test_barrier_source_ends_and_time_expiry(ending: str) -> None:
    try:
        setup, owner, _, _, _, _ = _cast()
        if ending == "incapacitated":
            owner.state.is_unconscious = True
        elif ending == "dead":
            owner.state.is_dead = True
        removed = cleanup_persistent_barriers(
            setup, 11 if ending == "expired" else 2,
        )
        assert removed
        assert setup.persistent_barriers == []
    except Exception:
        logger.exception("Barrier owner-expiry regression failed for %s.", ending)
        raise
