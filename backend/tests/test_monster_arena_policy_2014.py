from __future__ import annotations

import logging

from app.content.monster_catalog_2014 import unsupported_mechanics_2014
from app.content.monster_catalog_2014_action_support import unresolved_actions_2014, unresolved_reactions_2014
from app.content.monster_catalog_2014_arena_policy import (
    ARENA_OUT_OF_SCOPE_TRAITS_2014,
    ARENA_USABLE_MOVEMENT_TRAITS_2014,
    is_arena_disabled_action_2014,
    usable_movement_speed_2014,
)
from app.content.monster_catalog_2014_models import CatalogMonster2014

logger = logging.getLogger(__name__)


def _monster(
    *, action_names: list[str] | None = None, reaction_names: list[str] | None = None,
    unsupported_legendary_action_names: list[str] | None = None,
) -> CatalogMonster2014:
    try:
        return CatalogMonster2014(
            id="arena-policy-test",
            name="Arena Policy Test",
            ruleset="2014",
            size="medium",
            creature_type="monstrosity",
            armor_class=10,
            max_hp=10,
            speed={"walk": 30, "burrow": 40},
            abilities={"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10},
            action_names=action_names or [],
            reaction_names=reaction_names or [],
            unsupported_legendary_action_names=unsupported_legendary_action_names or [],
        )
    except Exception:
        logger.exception("Failed to build arena-policy test monster.")
        raise


def test_arena_disabled_actions_are_not_certification_blockers() -> None:
    try:
        source = _monster(action_names=[
            "Summon Fiend", "Teleport", "Plane Shift", "Banishment", "Etherealness", "Illusory Appearance",
        ])
        assert unresolved_actions_2014(source) == []
    except Exception:
        logger.exception("Arena-disabled action classification regression failed.")
        raise


def test_arena_disabled_reactions_are_not_certification_blockers() -> None:
    try:
        source = _monster(reaction_names=["Split"])
        assert unresolved_reactions_2014(source, set()) == []
    except Exception:
        logger.exception("Arena-disabled reaction classification regression failed.")
        raise


def test_arena_disabled_legendary_actions_are_not_certification_blockers() -> None:
    try:
        source = _monster(unsupported_legendary_action_names=["Teleport (Costs 2 Actions)", "Unmodeled Legendary"])
        blockers = unsupported_mechanics_2014(source)
        assert "legendary:Teleport (Costs 2 Actions)" not in blockers
        assert "legendary:Unmodeled Legendary" in blockers
    except Exception:
        logger.exception("Arena-disabled legendary-action classification regression failed.")
        raise


def test_unknown_combat_action_still_fails_closed() -> None:
    try:
        source = _monster(action_names=["Unmodeled Combat Blast"])
        assert unresolved_actions_2014(source) == ["Unmodeled Combat Blast"]
    except Exception:
        logger.exception("Unknown combat action fail-closed regression failed.")
        raise


def test_burrow_is_disabled_without_changing_other_movement_modes() -> None:
    try:
        assert usable_movement_speed_2014("burrow", 40) == 0
        assert usable_movement_speed_2014("fly", 60) == 60
        assert usable_movement_speed_2014("climb", 30) == 30
    except Exception:
        logger.exception("Arena movement policy regression failed.")
        raise


def test_explicit_arena_traits_are_preserved_as_nonblocking_provenance() -> None:
    try:
        disabled = {"Earth Glide", "Ethereal Jaunt", "Incorporeal Movement", "Siege Monster"}
        assert disabled <= ARENA_OUT_OF_SCOPE_TRAITS_2014
        assert "Spider Climb" in ARENA_USABLE_MOVEMENT_TRAITS_2014
        assert "Spider Climb" not in ARENA_OUT_OF_SCOPE_TRAITS_2014
        assert is_arena_disabled_action_2014("Summon Demon")
        assert not is_arena_disabled_action_2014("Multiattack")
    except Exception:
        logger.exception("Arena trait policy regression failed.")
        raise