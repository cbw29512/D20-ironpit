from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)

_ETHEREAL_JAUNT_IDS = ("phase-spider",)
_INCORPOREAL_MOVEMENT_IDS = ("banshee", "ghost", "specter", "will-o-wisp", "wraith")
_SINGLE_BLOCKER_UNLOCKS = ("phase-spider", "specter", "wraith")


def _source():
    try:
        return {monster.id: monster for monster in load_monster_source_2014()}
    except Exception:
        logger.exception("Failed to load 2014 source for arena-removed movement tests.")
        raise


def test_ethereal_and_incorporeal_movement_are_explicit_arena_neutral_traits() -> None:
    try:
        source = _source()
        assert {"Ethereal Jaunt", "Incorporeal Movement"} <= ARENA_NEUTRAL_TRAITS_2014
        for monster_id in _ETHEREAL_JAUNT_IDS:
            monster = source[monster_id]
            assert "Ethereal Jaunt" in monster.trait_names
            assert "Ethereal Jaunt" not in unsupported_traits_2014(monster)
        for monster_id in _INCORPOREAL_MOVEMENT_IDS:
            monster = source[monster_id]
            assert "Incorporeal Movement" in monster.trait_names
            assert "Incorporeal Movement" not in unsupported_traits_2014(monster)
    except Exception:
        logger.exception("Arena-removed ethereal/incorporeal trait classification failed.")
        raise


def test_single_trait_blockers_unlock_without_inventing_movement_state() -> None:
    try:
        source = _source()
        for monster_id in _SINGLE_BLOCKER_UNLOCKS:
            monster = source[monster_id]
            assert basic_blockers_2014(monster) == ()
            template = compile_combatant(adapt_basic_monster_2014(monster))
            assert set(monster.trait_names) <= set(template.source_trait_names)
            assert template.movement_modes.walk_ft == int(monster.speed.get("walk", 0))
            assert template.movement_modes.fly_ft == int(monster.speed.get("fly", 0))
    except Exception:
        logger.exception("Arena-removed movement unlock regression failed.")
        raise
