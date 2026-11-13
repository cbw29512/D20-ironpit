"""A standard frontline turn attacks without walking on the display grid."""
from __future__ import annotations

import logging

from app.combat.dice import SeededDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection

logger = logging.getLogger(__name__)


def test_standard_melee_turn_leaves_display_coordinates_unchanged():
    try:
        setup = build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-2014-l5"],
            monster_ids=["2014-goblin"], ruleset="2014",
        ))
        assert setup.arena_mode == "formation"
        hero, goblin = setup.heroes[0], setup.monsters[0]
        hero_position = hero.state.position.model_copy(deep=True)
        goblin_position = goblin.state.position.model_copy(deep=True)
        events, _ = resolve_combat_turn(
            1, 1, hero, goblin, setup, SeededDiceProvider(11),
        )
        assert any(event.event_type == "attack" for event in events)
        assert hero.state.position == hero_position
        assert goblin.state.position == goblin_position
        assert not any(
            event.animation == "movement" and (event.movement_ft or 0) > 0
            for event in events
        )
    except Exception:
        logger.exception("Standard formation attack turn moved a display card.")
        raise
