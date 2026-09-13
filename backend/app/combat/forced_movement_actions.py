from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.forced_movement_actions import ForcedMovementAction
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def legal_targets(
    source: EncounterCombatant,
    setup: EncounterSetup,
    action: ForcedMovementAction,
) -> list[EncounterCombatant]:
    try:
        if action.target_mode != "creatures_grappled_by_self":
            raise ValueError(f"Unsupported forced-movement target mode: {action.target_mode}")
        return [
            target for target in living_opponents(source, setup)
            if any(grapple.source_id == source.combatant_id for grapple in target.state.grapple_sources)
        ]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to select forced-movement targets for %s.", source.combatant_id)
        raise RuntimeError("Forced-movement targets could not be selected.") from exc


def resolve_action(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    action: ForcedMovementAction,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        for target in legal_targets(source, setup, action):
            before = combatant_distance(source, target)
            toward = action.direction == "toward_source"
            requested = min(action.distance_ft, before) if toward else action.distance_ft
            if requested <= 0:
                continue
            sign = -1 if target.position_ft >= source.position_ft else 1
            if not toward:
                sign *= -1
            start = target.position_ft
            target.position_ft = max(0, start + sign * requested)
            moved = abs(target.position_ft - start)
            if moved <= 0:
                continue
            after = combatant_distance(source, target)
            verb = "pulling" if toward else "pushing"
            direction = "toward" if toward else "away from"
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="movement",
                actor_id=source.combatant_id,
                actor_name=source.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                attack_name=action.name,
                distance_before_ft=before,
                distance_after_ft=after,
                movement_ft=moved,
                animation=action.animation,
                description=(
                    f"{source.state.template.name} uses {action.name}, {verb} "
                    f"{target.state.template.name} {moved} ft. {direction} itself."
                ),
            ))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Forced-movement action %s failed for %s.", action.id, source.combatant_id)
        raise RuntimeError("Forced-movement action could not be resolved.") from exc
