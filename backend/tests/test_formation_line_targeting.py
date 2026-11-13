"""Source line attacks cover one formation lane, not an arbitrary grid path."""
from __future__ import annotations

import logging

from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.area_targeting import member_in_area_placement
from app.combat.encounter_setup import build_encounter_setup
from app.domain.encounters import EncounterSelection

logger = logging.getLogger(__name__)


def test_source_acid_breath_honors_one_living_lane():
    try:
        setup = build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-2014-l5"] * 6,
            monster_ids=["2014-young-black-dragon"], ruleset="2014",
        ))
        assert setup.arena_mode == "formation"
        dragon = setup.monsters[0]
        action = next(row for row in dragon.state.template.saving_throw_actions
                      if row.area is not None and row.area.shape == "line")
        original = action.area.model_dump_json()
        front = [member for member in setup.heroes
                 if member.state.initial_formation_row == "front"]
        back = [member for member in setup.heroes
                if member.state.initial_formation_row == "back"]
        assert len(front) == len(back) == 3
        (placed,) = legal_area_save_placements(dragon, setup, action)
        assert placed.formation_only
        assert placed.target_ids == (front[0].combatant_id, back[0].combatant_id)
        assert member_in_area_placement(dragon, front[0], action.area, placed)
        assert not member_in_area_placement(dragon, front[1], action.area, placed)
        assert action.area.model_dump_json() == original

        # A fallen forward fighter must not make this line target inaccessible.
        front[0].state.is_alive = False
        front[0].state.is_dead = True
        front[0].state.current_hp = 0
        (after,) = legal_area_save_placements(dragon, setup, action)
        assert len(after.target_ids) == 2
        assert front[0].combatant_id not in after.target_ids
    except Exception:
        logger.exception("Source Acid Breath nonspatial line targeting failed.")
        raise
