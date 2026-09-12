from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.area_targeting import AreaPlacement, legal_area_placements
from app.combat.dice import DiceProvider
from app.combat.save_targets import resolve_save_targets, validate_save_targets
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def resolve_area_save_action(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    dice: DiceProvider,
    *,
    placement: AreaPlacement | None = None,
) -> tuple[list[BattleEvent], int, AreaPlacement]:
    """Preflight area geometry, spend one action, then resolve every affected enemy."""
    try:
        if action.area is None: raise ValueError(f"{action.name} does not define area geometry.")
        if not is_available(actor.state, "action"): raise ValueError("Action is not available for an area saving-throw action.")
        legal = legal_area_placements(actor, setup, action.area, action.range_ft)
        if not legal: raise ValueError(f"{action.name} has no legal area placement.")
        selected = placement or legal[0]
        if selected not in legal: raise ValueError(f"{action.name} received a stale or illegal area placement.")
        validate_save_targets(actor, setup, action, selected.target_ids, skip_range_check=True)
        spend(actor.state, "action")
        events, next_sequence = resolve_save_targets(
            sequence, round_number, actor, setup, action, selected.target_ids, dice,
            skip_range_check=True,
        )
        return events, next_sequence, selected
    except Exception:
        logger.exception("Failed area save action %s for %s.", action.id, actor.combatant_id)
        raise
