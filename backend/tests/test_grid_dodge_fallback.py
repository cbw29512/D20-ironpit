from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _gargantuan_commoner(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    try:
        template = build_commoner().model_copy(update={"size": CreatureSize.GARGANTUAN, "speed_ft": 30})
        state = build_combatant_state(template)
        state.position = GridPosition(x=x, y=y)
        return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)
    except Exception:
        logger.exception("Failed to build Gargantuan movement fixture %s.", combatant_id)
        raise


def _medium_target() -> EncounterCombatant:
    try:
        state = build_combatant_state(build_commoner())
        state.position = GridPosition(x=20, y=7)
        return EncounterCombatant(combatant_id="monster-target", side="monsters", position_ft=10, state=state)
    except Exception:
        logger.exception("Failed to build blocked-grid target fixture.")
        raise


def test_blocked_melee_only_gargantuan_dodges_instead_of_breaking() -> None:
    try:
        mover = _gargantuan_commoner("hero-mover", "heroes", 0, 6)
        wall = [
            _gargantuan_commoner("hero-wall-1", "heroes", 4, 0),
            _gargantuan_commoner("hero-wall-2", "heroes", 4, 4),
            _gargantuan_commoner("hero-wall-3", "heroes", 4, 8),
            _gargantuan_commoner("hero-wall-4", "heroes", 4, 12),
        ]
        target = _medium_target()
        setup = EncounterSetup(
            heroes=[mover, *wall],
            monsters=[target],
            hero_total_levels=1,
            monster_total_cr="0",
            map_definition=build_standard_iron_pit_map(),
        )

        events, _ = resolve_combat_turn(1, 1, mover, target, setup, FixedDiceProvider([]))

        assert not [event for event in events if event.event_type == "attack"]
        assert not [event for event in events if event.event_type == "movement"]
        dodge = next(event for event in events if event.feature_id == "dodge")
        assert dodge.event_type == "feature"
        assert mover.state.action_available is False
        assert mover.state.position == GridPosition(x=0, y=6)
    except Exception:
        logger.exception("Blocked Gargantuan Dodge fallback regression failed.")
        raise
