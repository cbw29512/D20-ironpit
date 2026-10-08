"""Noncombat Change Shape retains source provenance without blocking Pit combat."""

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_save_capabilities_2014 import unsupported_source_actions_2014

logger = logging.getLogger(__name__)


def test_adult_bronze_dragon_change_shape_is_arena_unavailable():
    try:
        dragon = next(row for row in load_monster_source_2014() if row.id == "adult-bronze-dragon")
        source_action_names = unsupported_source_actions_2014(dragon)
        assert any(name.casefold().startswith("change shape") for name in source_action_names)
        assert "source:extra-action" not in basic_blockers_2014(dragon)
        # The source action remains recorded and is never silently deleted.
        assert any(name.casefold().startswith("change shape") for name in dragon.action_names)
    except Exception:
        logger.exception("Adult Bronze Dragon arena-unavailable Change Shape regression failed")
        raise
