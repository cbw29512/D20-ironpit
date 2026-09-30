from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.area_save_healing import choose_area_healing_target, resolve_area_healing
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.area_targeting import AreaPlacement
from app.combat.grapple_queries import source_has_active_grapple
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.save_targets import resolve_save_targets
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def choose_area_save(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    *,
    action_cost: str | None = None,
) -> tuple[SavingThrowAction, AreaPlacement] | None:
    try:
        candidates = []
        for action in actor.state.template.saving_throw_actions:
            if action_cost is not None and action.action_cost != action_cost:
                continue
            if action.area is None or not action_resource_available(actor.state, action):
                continue
            if action.requires_no_active_grapple and source_has_active_grapple(setup, actor.combatant_id):
                continue
            for placement in legal_area_save_placements(actor, setup, action):
                heal_target = choose_area_healing_target(
                    actor, setup, action, placement,
                    require_wounded=not placement.target_ids,
                )
                if action.area_healing_rider is not None and heal_target is None:
                    continue
                candidates.append((action, placement, heal_target))
        if not candidates:
            return None
        action, placement, _ = max(
            candidates,
            key=lambda item: (
                len(item[1].target_ids),
                item[0].damage_dice_count,
                item[2] is not None,
                item[0].id,
            ),
        )
        return action, placement
    except Exception:
        logger.exception("Failed to choose area save action for %s.", actor.combatant_id)
        raise


def resolve_area_save(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    placement: AreaPlacement,
    dice,
) -> tuple[list[BattleEvent], int]:
    try:
        if action.area is None:
            raise ValueError(f"{action.name} has no area geometry.")
        if not is_available(actor.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is not available for {action.name}.")
        if not action_resource_available(actor.state, action):
            raise ValueError(f"{action.name} resource is unavailable.")
        if placement not in legal_area_save_placements(actor, setup, action):
            raise ValueError(f"{action.name} has a stale or illegal area placement.")
        heal_target = choose_area_healing_target(
            actor, setup, action, placement,
            require_wounded=not placement.target_ids,
        )
        if action.area_healing_rider is not None and heal_target is None:
            raise ValueError(f"{action.name} has no legal healing target in its area.")

        spend(actor.state, action.action_cost)
        if placement.target_ids:
            events, sequence = resolve_save_targets(
                sequence, round_number, actor, setup, action,
                placement.target_ids, dice, skip_range_check=True,
            )
            remaining = events[0].resource_remaining if events else None
        else:
            remaining = spend_action_resource(actor.state, action)
            events = []

        if heal_target is not None:
            event, sequence = resolve_area_healing(
                sequence, round_number, actor, heal_target, action, dice, remaining,
            )
            events.append(event)
        return events, sequence
    except Exception:
        logger.exception("Failed area save action %s for %s.", action.id, actor.combatant_id)
        raise
