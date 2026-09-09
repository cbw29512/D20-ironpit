from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def _targets(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    target_ids: tuple[str, ...],
    skip_range_check: bool,
) -> list[EncounterCombatant]:
    if not target_ids or len(set(target_ids)) != len(target_ids):
        raise ValueError("Multi-target save actions require unique target IDs.")
    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    expected_side = "monsters" if actor.side == "heroes" else "heroes"
    result: list[EncounterCombatant] = []
    for target_id in target_ids:
        target = by_id.get(target_id)
        if target is None:
            raise ValueError(f"Unknown save-action target {target_id!r}.")
        if target.side != expected_side:
            raise ValueError("Offensive Iron Pit save actions cannot target allies.")
        if not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0:
            raise ValueError(f"Save-action target {target_id!r} is not active.")
        distance_ft = 0 if skip_range_check else combatant_distance(actor, target)
        if not legal_save_action(action, target, distance_ft):
            raise ValueError(f"{action.name} cannot legally affect {target.state.template.name}.")
        result.append(target)
    return result


def resolve_save_targets(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    target_ids: tuple[str, ...],
    dice,
    *,
    skip_range_check: bool = False,
) -> tuple[list[BattleEvent], int]:
    """Resolve independent saves while sharing one damage roll across every target."""
    try:
        targets = _targets(actor, setup, action, target_ids, skip_range_check)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        events: list[BattleEvent] = []
        shared_damage_rolls: list[int] | None = None
        for target in targets:
            capture = [] if shared_damage_rolls is None and action.damage_dice_count else None
            event = resolve_save_action(
                sequence,
                round_number,
                actor,
                target,
                action,
                0 if skip_range_check else combatant_distance(actor, target),
                dice,
                spend_action=False,
                spend_resource_cost=False,
                shared_damage_rolls=shared_damage_rolls,
                capture_shared_damage_rolls=capture,
                affected_states=affected_states,
            )
            events.append(event)
            if capture is not None:
                if len(capture) != action.damage_dice_count:
                    raise RuntimeError("Shared damage roll was not established for every damage die.")
                shared_damage_rolls = capture
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed multi-target save resolution for %s.", action.id)
        raise
