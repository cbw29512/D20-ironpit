"""Formation promotion is an atomic team transition, not one creature per turn.

Data: EncounterSetup contains live states and each member's initial row.
State: a dead frontline causes every living backliner to become frontline at
once; display positions and immutable source rows remain unchanged.
"""
from __future__ import annotations

import logging

from app.combat.encounter_setup import build_encounter_setup
from app.combat.formation_rows import sync_formation_rows
from app.domain.models import EncounterSelection

logger = logging.getLogger(__name__)


def _setup(count: int):
    try:
        return build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-2014-l5"] * count,
            monster_ids=["2014-goblin"], ruleset="2014",
        ))
    except Exception:
        logger.exception("Could not build atomic promotion fixture.")
        raise


def _set_row(member, row: str) -> None:
    member.state.formation_row = row
    member.state.initial_formation_row = row


def _defeat(member) -> None:
    member.state.current_hp = 0
    member.state.is_alive = False
    member.state.is_dead = True


def test_three_backliners_with_no_frontline_promote_simultaneously():
    try:
        setup = _setup(3)
        for hero in setup.heroes:
            _set_row(hero, "back")
        positions = [hero.state.position.model_copy(deep=True) for hero in setup.heroes]
        promoted = sync_formation_rows(setup)
        assert [member.combatant_id for member in promoted] == [
            member.combatant_id for member in setup.heroes
        ]
        assert all(member.state.formation_row == "front" for member in setup.heroes)
        assert all(member.state.initial_formation_row == "back" for member in setup.heroes)
        assert [member.state.position for member in setup.heroes] == positions
        assert sync_formation_rows(setup) == []
    except Exception:
        logger.exception("Three no-frontline backliners were not promoted together.")
        raise


def test_living_frontline_blocks_all_promotion_then_all_backliners_step_up():
    try:
        setup = _setup(6)
        for member in setup.heroes[:3]:
            _set_row(member, "front")
        for member in setup.heroes[3:]:
            _set_row(member, "back")
        assert sync_formation_rows(setup) == []
        for member in setup.heroes[:2]:
            _defeat(member)
        assert sync_formation_rows(setup) == []
        _defeat(setup.heroes[2])
        promoted = sync_formation_rows(setup)
        assert [m.combatant_id for m in promoted] == [
            m.combatant_id for m in setup.heroes[3:]
        ]
        assert all(m.state.formation_row == "front" for m in setup.heroes[3:])
        assert all(m.state.initial_formation_row == "back" for m in setup.heroes[3:])
    except Exception:
        logger.exception("Frontline-collapse group transition was incorrect.")
        raise
