"""Keep noncombat Change Shape on source cards without blocking any matching dragon."""

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_save_capabilities_2014 import unsupported_source_actions_2014

logger = logging.getLogger(__name__)


CHANGE_SHAPE_ONLY_DRAGONS = (
    "adult-bronze-dragon",
    "adult-gold-dragon",
    "adult-silver-dragon",
    "ancient-brass-dragon",
    "ancient-bronze-dragon",
    "ancient-copper-dragon",
    "ancient-gold-dragon",
    "ancient-silver-dragon",
)


def test_noncombat_change_shape_kept_in_source_and_not_a_blocker():
    try:
        by_id = {row.id: row for row in load_monster_source_2014()}
        for monster_id in CHANGE_SHAPE_ONLY_DRAGONS:
            dragon = by_id[monster_id]
            assert any(name.casefold().startswith("change shape") for name in dragon.action_names)
            assert any(name.casefold().startswith("change shape") for name in unsupported_source_actions_2014(dragon))
            assert not basic_blockers_2014(dragon), (monster_id, basic_blockers_2014(dragon))
    except Exception:
        logger.exception("2014 Change Shape family regression failed")
        raise
