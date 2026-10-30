from __future__ import annotations

import logging
from typing import Any

from app.domain.models import CombatantTemplate
from browser_action_serializer import defense_row, healing_row, removal_row, spell_attack_row, spell_save_row
from browser_template_common_serializer import automatic_spell_row
from browser_timed_self_buff_serializer import timed_self_buff_row

logger = logging.getLogger(__name__)


def extend_action_rows(row: dict[str, Any], template: CombatantTemplate) -> None:
    try:
        if template.spell_save_actions:
            row["spell_save_actions"] = [spell_save_row(item) for item in template.spell_save_actions]
        if template.spell_attack_actions:
            row["spell_attack_actions"] = [spell_attack_row(item) for item in template.spell_attack_actions]
        if template.automatic_spell_actions:
            row["automatic_spell_actions"] = [
                automatic_spell_row(item) for item in template.automatic_spell_actions
            ]
        if template.defensive_spell_actions:
            row["defensive_spell_actions"] = [defense_row(item) for item in template.defensive_spell_actions]
        if template.timed_self_buff_actions:
            row["timed_self_buff_actions"] = [
                timed_self_buff_row(item) for item in template.timed_self_buff_actions
            ]
        if template.healing_actions:
            row["healingActions"] = [healing_row(item) for item in template.healing_actions]
        if template.condition_removal_actions:
            row["condition_removal_actions"] = [
                removal_row(item) for item in template.condition_removal_actions
            ]
        if template.attack_action:
            row["attack_action"] = {
                "id": template.attack_action.id,
                "name": template.attack_action.name,
                "slots": [
                    {
                        "attackIds": slot.attack_ids,
                        "saveActionIds": slot.save_action_ids,
                        "forcedMovementActionIds": slot.forced_movement_action_ids,
                    }
                    for slot in template.attack_action.slots
                ],
            }
    except Exception:
        logger.exception("Failed spell/action serialization for %s.", template.id)
        raise
