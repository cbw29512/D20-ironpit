"""All Iron Pit teleport actions require a real effect to clear before spending."""
from __future__ import annotations

import logging

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.teleport_policy import choose_teleport_action
from app.combat.teleport_resolution import resolve_teleport
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_commoner
from app.content.shared_teleport_spells_2014 import dimension_door_2014
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def _member(template, combatant_id, side, x, y, slots=None):
    try:
        resources = list(template.resources)
        for level, count in (slots or {}).items():
            resources.append(ResourceDefinition(
                id=f"spell-slot-{level}", name=f"Level {level} Slot", max_uses=count,
            ))
        state = build_combatant_state(template.model_copy(update={"resources": resources}))
        state.position = GridPosition(x=x, y=y)
        return EncounterCombatant(
            combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
        )
    except Exception:
        logger.exception("Failed to build teleport no-op test combatant %s.", combatant_id)
        raise


def test_dimension_door_noop_is_rejected_without_spending():
    try:
        caster = _member(build_karnok_stoneward().model_copy(update={
            "teleport_actions": [dimension_door_2014()],
            "resources": [ResourceDefinition(
                id="spell-slot-4", name="4th-level Slot", max_uses=1,
            )],
            "max_hp": 40,
        }), "caster", "heroes", 1, 2, {4: 1})
        enemy = _member(build_commoner(), "enemy", "monsters", 8, 2)
        setup = EncounterSetup(
            heroes=[caster], monsters=[enemy], hero_total_levels=1,
            monster_total_cr="1/4", ruleset="2014",
            map_definition=build_standard_iron_pit_map(),
        )
        origin = GridPosition(x=1, y=2)
        slot = next(item for item in caster.state.resources if item.id == "spell-slot-4")

        assert choose_teleport_action(caster, setup, "1:caster") is None
        with pytest.raises(ValueError, match="no active teleport-cancelable effect"):
            resolve_teleport(
                1, 1, caster, setup, dimension_door_2014(),
                GridPosition(x=7, y=2), FixedDiceProvider([1, 1, 1, 1]),
                "1:caster",
            )

        assert caster.state.position == origin
        assert caster.state.current_hp == 40
        assert caster.state.action_available is True
        assert slot.current_uses == 1
    except Exception:
        logger.exception("Dimension Door no-op guard regression failed.")
        raise
