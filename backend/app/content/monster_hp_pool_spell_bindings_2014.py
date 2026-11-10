"""2014 monster spell access -> shared typed HP-pool spell action."""
from __future__ import annotations

import logging

from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_prepared_spells_2014 import _prepared_spells
from app.content.monster_source_2014 import SourceMonster2014
from app.content.shared_hp_pool_spells_2014 import sleep_2014
from app.domain.hit_point_pool_spells import HitPointPoolSpellAction

logger = logging.getLogger(__name__)


def innate_hp_pool_spells_2014(monster: SourceMonster2014) -> list[HitPointPoolSpellAction]:
    """Match printed 2014 innate spell access; spell mechanics come from pinned source."""
    try:
        return [sleep_2014() for row in innate_spells_2014(monster)
                if row.get("id") == "sleep"]
    except Exception:
        logger.exception("Failed 2014 innate HP-pool spell binding for %s.", monster.id)
        raise


def prepared_hp_pool_spells_2014(monster: SourceMonster2014) -> list[HitPointPoolSpellAction]:
    """Bind the same spell to prepared slots without duplicating its mechanics."""
    try:
        return [sleep_2014() for row in _prepared_spells(monster)
                if row.get("id") == "sleep"]
    except Exception:
        logger.exception("Failed 2014 prepared HP-pool spell binding for %s.", monster.id)
        raise
