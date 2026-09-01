from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_tactical_shift(
    sequence: int,
    round_number: int,
    fighter: EncounterCombatant,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Use Fighter 5 Tactical Shift as OA-free bonus movement after Second Wind."""
    try:
        fraction = fighter.state.template.progression_features.tactical_shift_fraction
        if fraction <= 0 or fighter.state.is_dead or fighter.state.is_unconscious:
            return None
        target = select_nearest_target(fighter, setup)
        if target is None:
            return None
        before = combatant_distance(fighter, target)
        allowance = int(fighter.state.template.speed_ft * fraction)
        moved = min(max(0, before - 5), allowance)
        if moved <= 0:
            return None
        direction = 1 if fighter.position_ft < target.position_ft else -1
        fighter.position_ft += direction * moved
        after = combatant_distance(fighter, target)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="movement",
            actor_id=fighter.combatant_id,
            actor_name=fighter.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            distance_before_ft=before,
            distance_after_ft=after,
            movement_ft=moved,
            feature_id="tactical-shift",
            animation="advance",
            description=f"{fighter.state.template.name} uses Tactical Shift to move {moved} feet without provoking Opportunity Attacks.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Tactical Shift failed for %s.", fighter.combatant_id)
        raise RuntimeError("Tactical Shift could not be resolved.") from exc
