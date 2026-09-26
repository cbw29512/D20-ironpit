from __future__ import annotations

import logging

from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_form_2014
from app.domain.replacement_form_actions import ReplacementFormAction

logger = logging.getLogger(__name__)


def wild_shape_action_2014(level: int) -> ReplacementFormAction:
    try:
        form = canonical_wild_shape_form_2014(level)
        return ReplacementFormAction(
            id="wild-shape",
            name="Wild Shape",
            action_cost="action",
            form_template_id=form.monster_id,
            resource_id="wild-shape",
            resource_cost=1,
            voluntary_revert_action="bonus_action",
            retain_spellcasting=level >= 18,
            source="D&D Basic Rules 2014: Druid — Wild Shape",
        )
    except Exception:
        logger.exception("Failed to build 2014 Wild Shape action at level %s.", level)
        raise
