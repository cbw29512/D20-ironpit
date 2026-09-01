from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import effective_speed
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def move_toward_combatant(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    target: EncounterCombatant,
    desired_distance_ft: int,
) -> BattleEvent | None:
    try:
        if desired_distance_ft < 0:
            raise ValueError("Desired distance cannot be negative.")
        before = combatant_distance(mover, target)
        needed = max(0, before - desired_distance_ft)
        moved = min(needed, mover.state.movement_remaining_ft)
        if moved <= 0:
            return None

        direction = 1 if mover.position_ft < target.position_ft else -1
        mover.position_ft += direction * moved
        mover.state.movement_remaining_ft -= moved
        after = combatant_distance(mover, target)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="movement",
            actor_id=mover.combatant_id,
            actor_name=mover.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            distance_before_ft=before,
            distance_after_ft=after,
            movement_ft=moved,
            animation="advance",
            description=f"{mover.state.template.name} advances {moved} feet.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Encounter movement failed for %s.", mover.combatant_id)
        raise RuntimeError("Encounter movement could not be resolved.") from exc


def take_encounter_dash(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    target: EncounterCombatant,
) -> BattleEvent:
    try:
        if not is_available(mover.state, "action"):
            raise ValueError("Action is not available for Dash.")
        before = combatant_distance(mover, target)
        speed = effective_speed(mover.state)
        spend(mover.state, "action")
        mover.state.movement_remaining_ft += speed
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="dash",
            actor_id=mover.combatant_id,
            actor_name=mover.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            distance_before_ft=before,
            distance_after_ft=before,
            movement_ft=speed,
            animation="dash",
            description=f"{mover.state.template.name} takes the Dash action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Encounter Dash failed for %s.", mover.combatant_id)
        raise RuntimeError("Encounter Dash could not be resolved.") from exc
