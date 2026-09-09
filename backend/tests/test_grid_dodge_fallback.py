from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _commoner(
    combatant_id: str,
    side: str,
    x: int,
    y: int,
    *,
    size: CreatureSize = CreatureSize.MEDIUM,
) -> EncounterCombatant:
    try:
        template = build_commoner().model_copy(update={"size": size, "speed_ft": 30})
        state = build_combatant_state(template)
        state.position = GridPosition(x=x, y=y)
        return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)
    except Exception:
        logger.exception("Failed to build blocked-offense fixture %s.", combatant_id)
        raise


def _target(x: int = 20, y: int = 7) -> EncounterCombatant:
    try:
        return _commoner("monster-target", "monsters", x, y)
    except Exception:
        logger.exception("Failed to build blocked-grid target fixture.")
        raise


def _setup(mover: EncounterCombatant, target: EncounterCombatant, allies: list[EncounterCombatant]) -> EncounterSetup:
    try:
        return EncounterSetup(
            heroes=[mover, *allies],
            monsters=[target],
            hero_total_levels=1,
            monster_total_cr="0",
            map_definition=build_standard_iron_pit_map(),
        )
    except Exception:
        logger.exception("Failed to build Dodge fallback encounter fixture.")
        raise


def _assert_dodge_only(mover: EncounterCombatant, target: EncounterCombatant, allies: list[EncounterCombatant]) -> None:
    try:
        setup = _setup(mover, target, allies)
        before = mover.state.position.model_copy(deep=True)
        events, _ = resolve_combat_turn(1, 1, mover, target, setup, FixedDiceProvider([1]))
        assert not [event for event in events if event.event_type == "attack"]
        assert not [event for event in events if event.event_type == "movement"]
        dodge = next(event for event in events if event.feature_id == "dodge")
        assert dodge.event_type == "feature"
        assert mover.state.action_available is False
        assert mover.state.position == before
    except Exception:
        logger.exception("Blocked-offense Dodge fallback assertion failed for %s.", mover.combatant_id)
        raise


def test_open_melee_path_advances_then_dodges_when_attack_is_not_reachable_this_turn() -> None:
    try:
        mover = _commoner("hero-approach", "heroes", 0, 7)
        target = _target(9, 7)
        setup = _setup(mover, target, [])
        begin_turn(mover.state)
        events, _ = resolve_combat_turn(1, 1, mover, target, setup, FixedDiceProvider([1]))
        movement = [event for event in events if event.event_type == "movement"]
        assert sum(event.movement_cost_ft or 0 for event in movement) == 30
        assert mover.state.position == GridPosition(x=6, y=7)
        assert not [event for event in events if event.event_type == "attack"]
        assert any(event.feature_id == "dodge" for event in events)
    except Exception:
        logger.exception("Useful multi-turn melee approach regression failed.")
        raise


def test_blocked_melee_only_gargantuan_dodges_instead_of_breaking() -> None:
    try:
        mover = _commoner("hero-mover", "heroes", 0, 6, size=CreatureSize.GARGANTUAN)
        wall = [
            _commoner("hero-wall-1", "heroes", 4, 0, size=CreatureSize.GARGANTUAN),
            _commoner("hero-wall-2", "heroes", 4, 4, size=CreatureSize.GARGANTUAN),
            _commoner("hero-wall-3", "heroes", 4, 8, size=CreatureSize.GARGANTUAN),
            _commoner("hero-wall-4", "heroes", 4, 12, size=CreatureSize.GARGANTUAN),
        ]
        _assert_dodge_only(mover, _target(), wall)
    except Exception:
        logger.exception("Blocked Gargantuan Dodge fallback regression failed.")
        raise


def test_medium_melee_creature_surrounded_target_by_summoned_allies_dodges() -> None:
    try:
        mover = _commoner("hero-medium-mover", "heroes", 0, 7)
        target = _target(7, 7)
        summons = [
            _commoner("summon-top", "heroes", 6, 4, size=CreatureSize.HUGE),
            _commoner("summon-left", "heroes", 6, 7),
            _commoner("summon-right", "heroes", 8, 7),
            _commoner("summon-bottom", "heroes", 6, 8, size=CreatureSize.HUGE),
        ]
        _assert_dodge_only(mover, target, summons)
    except Exception:
        logger.exception("Blocked Medium summon-ring Dodge fallback regression failed.")
        raise
