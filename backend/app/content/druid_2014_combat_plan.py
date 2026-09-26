from __future__ import annotations

import logging
from dataclasses import dataclass

from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_form_2014

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Druid2014CombatPlan:
    opening_buff_id: str
    concentration_spell_id: str
    wild_shape_form_id: str
    opening_buff_before_initiative: bool = True
    concentration_before_wild_shape: bool = True


def druid_2014_combat_plan(level: int) -> Druid2014CombatPlan:
    try:
        if level < 2 or level > 20:
            raise ValueError("2014 Druid Wild Shape combat plan covers levels 2 through 20.")
        form = canonical_wild_shape_form_2014(level)
        return Druid2014CombatPlan(
            opening_buff_id="longstrider",
            concentration_spell_id="faerie-fire",
            wild_shape_form_id=form.monster_id,
        )
    except Exception:
        logger.exception("Failed to build 2014 Druid combat plan at level %s.", level)
        raise
