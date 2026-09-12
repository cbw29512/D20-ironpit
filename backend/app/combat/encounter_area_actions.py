from __future__ import annotations

import logging

from app.combat.area_save_actions import resolve_area_save_action
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.resources import action_resource_available, resource_definition
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _is_recharge_action(attacker: EncounterCombatant, action) -> bool:
    if action.resource_id is None:
        return False
    definition = resource_definition(attacker.state, action.resource_id)
    return definition is not None and definition.recharge is not None


def area_save_choice(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    *,
    recharge_only: bool = False,
):
    """Choose the legal action-aware area placement hitting the most eligible enemies."""
    try:
        choices = []
        for action in attacker.state.template.saving_throw_actions:
            if action.area is None or not action_resource_available(attacker.state, action):
                continue
            if recharge_only and not _is_recharge_action(attacker, action):
                continue
            placements = legal_area_save_placements(attacker, setup, action)
            if placements:
                choices.append((len(placements[0].target_ids), action.id, action, placements[0]))
        if not choices:
            return None
        _, _, action, placement = max(choices, key=lambda row: (row[0], row[1]))
        return action, placement
    except Exception:
        logger.exception("Failed area save-action choice for %s.", attacker.combatant_id)
        raise


def resolve_ready_area_action(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    *,
    recharge_only: bool = False,
):
    try:
        choice = area_save_choice(attacker, setup, recharge_only=recharge_only)
        if choice is None:
            return [], sequence, False
        action, placement = choice
        events, sequence, _ = resolve_area_save_action(
            sequence, round_number, attacker, setup, action, dice, placement=placement,
        )
        return events, sequence, True
    except Exception:
        logger.exception("Failed area save-action resolution for %s.", attacker.combatant_id)
        raise
