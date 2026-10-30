from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014, save_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_limited_audible_conditions_2014 import (
    source_proven_limited_audible_conditions_2014,
)

logger = logging.getLogger(__name__)


def _vrock():
    try:
        return next(item for item in load_monster_source_2014() if item.name == "Vrock")
    except Exception:
        logger.exception("Failed to load the 2014 Vrock source card.")
        raise


def test_vrock_stunning_screech_uses_generic_limited_audible_control() -> None:
    try:
        monster = _vrock()
        actions = source_proven_limited_audible_conditions_2014(monster)
        assert len(actions) == 1

        action = actions[0]
        assert action.id == "stunning-screech"
        assert action.name == "Stunning Screech"
        assert action.save_ability == "constitution"
        assert action.dc == 14
        assert action.range_ft == 20
        assert action.target_scope == "all-other-creatures"
        assert action.requires_target_hearing is True
        assert action.excluded_target_creature_types == ["demon"]
        assert action.resource_id == "stunning-screech"
        assert action.resource_cost == 1
        assert action.area is not None
        assert (action.area.shape, action.area.radius_ft) == ("emanation", 20)

        rider = action.failed_save_timed_effect
        assert rider is not None
        assert rider.effect_id == "stunned"
        assert rider.duration_rounds == 1
        assert rider.expiry_timing == "source_turn_end"
    except Exception:
        logger.exception("Vrock Stunning Screech source-binding regression failed.")
        raise


def test_vrock_limited_audible_control_uses_shared_resource_and_clears_extra_action() -> None:
    try:
        monster = _vrock()
        actions = {item.id for item in save_capabilities_2014(monster)}
        assert {"spores", "stunning-screech"} <= actions

        resources = {item.id: item.max_uses for item in save_resources_2014(monster)}
        assert resources["spores"] == 1
        assert resources["stunning-screech"] == 1

        blockers = basic_blockers_2014(monster)
        assert "mechanic:recharge" not in blockers
        assert "source:extra-action" not in blockers
    except Exception:
        logger.exception("Vrock limited-audible blocker regression failed.")
        raise
