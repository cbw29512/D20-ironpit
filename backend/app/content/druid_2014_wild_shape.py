from __future__ import annotations

import logging

from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_form_2014
from app.domain.replacement_form_actions import ReplacementFormAction

logger = logging.getLogger(__name__)

_BEAST_SPELL_ACTION_IDS = [
    "produce-flame",
    "poison-spray",
    "faerie-fire",
    "healing-word",
    "cure-wounds",
    "lesser-restoration",
    "dispel-magic",
]
_ARCHDRUID_SPELL_ACTION_IDS = [
    *_BEAST_SPELL_ACTION_IDS,
    "longstrider",
    "barkskin",
    "freedom-of-movement",
]


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
            retained_spell_action_ids=(
                list(_ARCHDRUID_SPELL_ACTION_IDS)
                if level >= 20
                else list(_BEAST_SPELL_ACTION_IDS) if level >= 18 else []
            ),
            setup_spell_id="faerie-fire",
            source="D&D Basic Rules 2014: Druid — Wild Shape",
        )
    except Exception:
        logger.exception("Failed to build 2014 Wild Shape action at level %s.", level)
        raise
