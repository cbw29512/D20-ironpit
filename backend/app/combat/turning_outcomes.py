from __future__ import annotations

import logging
from fractions import Fraction

from app.combat.dice import DiceProvider
from app.combat.zero_hp import reduce_to_zero_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def challenge_rating_at_or_below(
    target: EncounterCombatant,
    maximum_cr: str | None,
) -> bool:
    """Compare printed monster CR against a source-defined turning threshold."""
    try:
        challenge_rating = target.state.template.challenge_rating
        if maximum_cr is None or challenge_rating is None:
            return False
        return Fraction(challenge_rating) <= Fraction(maximum_cr)
    except Exception as exc:
        logger.exception(
            "Failed turning CR comparison for %s against %s.",
            target.state.template.name,
            maximum_cr,
        )
        raise ValueError(
            f"Invalid turning-destruction Challenge Rating comparison for {target.state.template.name}."
        ) from exc


def destroy_on_failed_turn_save_if_eligible(
    target: EncounterCombatant,
    *,
    succeeded: bool,
    maximum_cr: str | None,
    dice: DiceProvider,
    affected_states: list[CombatantState],
) -> bool:
    """Apply a generic failed-turn-save destruction rider without damage semantics."""
    try:
        if succeeded or target.state.is_dead:
            return False
        if not challenge_rating_at_or_below(target, maximum_cr):
            return False
        reduce_to_zero_hit_points(
            target.state,
            dice=dice,
            affected_states=affected_states,
        )
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed turning destruction outcome for %s.",
            target.state.template.name,
        )
        raise RuntimeError("Turning destruction outcome could not be resolved.") from exc
