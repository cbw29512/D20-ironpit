from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.flight_ground_immunity import combatant_is_flying
from app.combat.grid_geometry import footprint_side_squares
from app.combat.grid_pathing import plan_movement_toward
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.combat.pit_engagement import voluntary_destination_leaves_melee
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition

logger = logging.getLogger(__name__)

_FLYBY_IDS = ("flying-snake", "giant-owl", "owl", "pteranodon")


def _source():
    try:
        return {monster.id: monster for monster in load_monster_source_2014()}
    except Exception:
        logger.exception("Failed to load 2014 monster source for Flyby tests.")
        raise


def _compile(monster_id: str):
    try:
        monster = _source()[monster_id]
        return compile_combatant(adapt_basic_monster_2014(monster))
    except Exception:
        logger.exception("Failed to compile 2014 Flyby monster %s.", monster_id)
        raise


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    try:
        state = build_combatant_state(template)
        state.position = GridPosition(x=x, y=y)
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=x * 5,
            state=state,
        )
    except Exception:
        logger.exception("Failed to place Flyby encounter member %s.", combatant_id)
        raise


def test_flyby_stays_arena_neutral_because_pit_overrides_leave_reach() -> None:
    try:
        source = _source()
        for monster_id in _FLYBY_IDS:
            monster = source[monster_id]
            assert "Flyby" in monster.trait_names
            assert "Flyby" in ARENA_NEUTRAL_TRAITS_2014
            assert "Flyby" not in bound_trait_names_2014(monster)
            assert "Flyby" not in unsupported_traits_2014(monster)
            assert basic_blockers_2014(monster) == ()
            template = _compile(monster_id)
            assert template.movement_modes.fly_ft == 60
            assert template.environment_context_reactions == []
    except Exception:
        logger.exception("2014 Flyby arena-neutral classification regression failed.")
        raise


def test_flyby_creatures_stay_in_melee_and_cannot_kite() -> None:
    try:
        map_definition = BattleMapDefinition(id="flyby-lock", width_squares=16, height_squares=16)
        hero_template = build_karnok_stoneward_2014(1)
        for monster_id in _FLYBY_IDS:
            flyer_template = _compile(monster_id)
            side = footprint_side_squares(flyer_template.size)
            flyer = _member(flyer_template, monster_id, "monsters", 6, 6)
            hero = _member(hero_template, "karnok", "heroes", 6 + side, 6)
            members = [flyer, hero]
            away = GridPosition(x=4, y=6)
            assert combatant_is_flying(flyer.state) is True
            assert voluntary_destination_leaves_melee(flyer, members, away) is True
            plan = plan_movement_toward(map_definition, flyer, hero, members, 40, 60)
            assert plan.path == []
            assert flyer.state.position == GridPosition(x=6, y=6)
    except Exception:
        logger.exception("2014 Flyby pit-engagement regression failed.")
        raise


def test_flyby_does_not_exempt_opportunity_attacks_when_leaving_reach() -> None:
    try:
        hero_template = build_karnok_stoneward_2014(1)
        for monster_id in _FLYBY_IDS:
            flyer = _member(_compile(monster_id), monster_id, "monsters", 1, 1)
            hero = _member(hero_template, "karnok", "heroes", 2, 1)
            setup = EncounterSetup(
                heroes=[hero], monsters=[flyer], hero_total_levels=1, monster_total_cr="0", ruleset="2014",
            )
            event = resolve_opportunity_attack(
                1, 1, hero, flyer, setup, 5, 10, "speed", FixedDiceProvider([2]),
            )
            assert event is not None
            assert event.feature_id == "opportunity-attack"
            assert hero.state.reaction_available is False
    except Exception:
        logger.exception("2014 Flyby opportunity-attack exemption regression failed.")
        raise
