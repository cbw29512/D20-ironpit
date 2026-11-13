"""Formation cones reach the exposed enemy line, with no grid placement."""
from __future__ import annotations

import logging

from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.area_targeting import member_in_area_placement
from app.combat.encounter_setup import build_encounter_setup
from app.combat.formation_engagement import effective_row
from app.domain.encounters import EncounterSelection

logger = logging.getLogger(__name__)


def _encounter():
    try:
        return build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-2014-l5"] * 4,
            monster_ids=["2014-hell-hound"], ruleset="2014",
        ))
    except Exception:
        logger.exception("Formation cone encounter construction failed.")
        raise


def test_source_fire_breath_hits_exposed_frontline_not_backline():
    try:
        setup = _encounter()
        assert setup.arena_mode == "formation"
        hound = setup.monsters[0]
        action = next(
            row for row in hound.state.template.saving_throw_actions
            if row.area is not None and row.area.shape == "cone"
        )
        # Preserve source dimensions: only target coverage is nonspatial.
        printed = action.area.model_dump_json()
        front = [hero for hero in setup.heroes if effective_row(hero, setup) == "front"]
        back = [hero for hero in setup.heroes if effective_row(hero, setup) == "back"]
        assert len(front) == 3 and len(back) == 1
        (placement,) = legal_area_save_placements(hound, setup, action)
        assert placement.formation_only
        assert set(placement.target_ids) == {hero.combatant_id for hero in front}
        assert all(member_in_area_placement(hound, hero, action.area, placement)
                   for hero in front)
        assert not any(member_in_area_placement(hound, hero, action.area, placement)
                       for hero in back)
        assert action.area.model_dump_json() == printed

        # Immediate promotion changes the live target group even without a
        # movement event or physical display-position change.
        for hero in front:
            hero.state.is_dead = True
            hero.state.is_alive = False
            hero.state.current_hp = 0
        assert effective_row(back[0], setup) == "front"
        (promoted,) = legal_area_save_placements(hound, setup, action)
        assert promoted.target_ids == (back[0].combatant_id,)
        assert promoted.formation_only
    except Exception:
        logger.exception("Source cone formation targeting regression failed.")
        raise
