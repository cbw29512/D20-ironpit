from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.grapple_queries import source_has_active_grapple
from app.combat.resources import action_resource_available
from app.combat.save_targets import resolve_save_targets
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def choose_area_save(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[SavingThrowAction, object] | None:
    try:
        candidates = []
        for action in actor.state.template.saving_throw_actions:
            if action.area is None or not action_resource_available(actor.state, action):
                continue
            if action.requires_no_active_grapple and source_has_active_grapple(setup, actor.combatant_id):
                continue
            placements = legal_area_save_placements(actor, setup, action)
            if placements:
                candidates.append((action, placements[0]))
        if not candidates:
            return None
        return max(candidates, key=lambda item: (len(item[1].target_ids), item[0].damage_dice_count, item[0].id))
    except Exception:
        logger.exception("Failed to choose area save action for %s.", actor.combatant_id)
        raise


def resolve_area_save(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    placement,
    dice,
) -> tuple[list[BattleEvent], int]:
    try:
        if action.area is None:
            raise ValueError(f"{action.name} has no area geometry.")
        if not is_available(actor.state, "action"):
            raise ValueError("Action is not available for area save.")
        legal = legal_area_save_placements(actor, setup, action)
        if placement not in legal:
            raise ValueError(f"{action.name} has a stale or illegal area placement.")
        spend(actor.state, "action")
        return resolve_save_targets(
            sequence, round_number, actor, setup, action,
            placement.target_ids, dice, skip_range_check=True,
        )
    except Exception:
        logger.exception("Failed area save action %s for %s.", action.id, actor.combatant_id)
        raise
