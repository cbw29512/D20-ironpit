from __future__ import annotations

import logging

from app.content.druid_2024_endgame import BEAST_SPELL_ACTION_IDS
from app.domain.replacement_form_actions import ReplacementFormAction

logger = logging.getLogger(__name__)


def wild_shape_actions(level: int) -> list[ReplacementFormAction]:
    try:
        if level < 2:
            return []
        form_template_id = "srd-brown-bear" if level >= 8 else "srd-wolf"
        return [ReplacementFormAction(
            id="wild-shape",
            name="Wild Shape",
            action_cost="bonus_action",
            form_template_id=form_template_id,
            resource_id="wild-shape",
            resource_cost=1,
            voluntary_revert_action="bonus_action",
            hp_mode="retain_owner",
            temporary_hp_on_enter=level,
            retain_creature_type=True,
            ends_on_incapacitated=True,
            replace_existing_form=True,
            retain_spellcasting=level >= 18,
            retained_spell_action_ids=(list(BEAST_SPELL_ACTION_IDS) if level >= 18 else []),
            ai_use_policy="emergency_only",
            source="D&D Beyond Basic Rules 2024: Druid — Wild Shape",
        )]
    except Exception:
        logger.exception("Failed to build 2024 Wild Shape at Druid level %s.", level)
        raise
