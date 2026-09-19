from __future__ import annotations

from dataclasses import dataclass
import logging

from app.domain.reactions import DamageReactionAttack

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DamageReactionTrigger:
    """Runtime facts required to prove a damage-triggered reaction is legal."""

    applied_damage: int
    source_is_creature: bool
    source_distance_ft: int
    reaction_available: bool
    reactor_can_react: bool


def damage_reaction_is_eligible(
    policy: DamageReactionAttack | None,
    trigger: DamageReactionTrigger,
) -> bool:
    """Fail closed unless every universal damage-reaction prerequisite is proven."""
    try:
        if policy is None:
            return False
        if trigger.applied_damage <= 0:
            return False
        if not trigger.source_is_creature:
            return False
        if trigger.source_distance_ft < 0:
            logger.warning("Rejecting damage reaction with negative source distance: %s", trigger.source_distance_ft)
            return False
        if trigger.source_distance_ft > policy.source_range_ft:
            return False
        if not trigger.reaction_available or not trigger.reactor_can_react:
            return False
        return True
    except (AttributeError, TypeError, ValueError):
        logger.exception("Damage reaction eligibility evaluation failed closed")
        return False
