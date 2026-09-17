from __future__ import annotations

import logging

from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_activation_movement(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    *,
    speed_fraction: float,
    desired_distance_ft: int = 5,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve optional movement granted by activating a feature without spending normal turn movement."""
    try:
        if speed_fraction <= 0 or speed_fraction > 1:
            raise ValueError("Activation movement speed_fraction must be in (0, 1].")
        opponents = setup.monsters if mover.side == "heroes" else setup.heroes
        living = [member for member in opponents if not member.state.is_dead and not member.state.is_unconscious]
        if not living:
            return [], sequence
        target = min(living, key=lambda member: (abs(member.position_ft - mover.position_ft), member.combatant_id))
        allowance = int(mover.state.template.speed_ft * speed_fraction)
        if allowance <= 0:
            return [], sequence

        normal_remaining = mover.state.movement_remaining_ft
        mover.state.movement_remaining_ft = normal_remaining + allowance
        try:
            events, sequence, _ = move_toward_with_reactions(
                sequence,
                round_number,
                mover,
                target,
                setup,
                desired_distance_ft,
                dice,
                turn_key=turn_key,
            )
        finally:
            mover.state.movement_remaining_ft = normal_remaining
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Activation movement failed for %s.", mover.combatant_id)
        raise RuntimeError("Activation-triggered movement could not be resolved.") from exc
