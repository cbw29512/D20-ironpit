from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.resources import resource_available, spend_resource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import DiceRoll, RollRevision

logger = logging.getLogger(__name__)


def _candidate_sources(
    roller: EncounterCombatant,
    setup: EncounterSetup,
    succeeded: bool,
) -> list[EncounterCombatant]:
    desired_side = roller.side if not succeeded else ("monsters" if roller.side == "heroes" else "heroes")
    candidates: list[EncounterCombatant] = []
    for member in [*setup.heroes, *setup.monsters]:
        rule = member.state.template.progression_features.d20_outcome_adjustment
        if member.side != desired_side or rule is None:
            continue
        if member.state.is_dead or not member.state.is_alive or member.state.current_hp <= 0:
            continue
        if is_incapacitated(member.state) or not resource_available(member.state, rule.resource_id):
            continue
        if combatant_distance(member, roller) <= rule.range_ft:
            candidates.append(member)
    return sorted(candidates, key=lambda member: (combatant_distance(member, roller), member.combatant_id))


def _reversal_gap(total: int, target_number: int, succeeded: bool) -> int:
    return total - target_number + 1 if succeeded else target_number - total


def adjust_d20_outcome(
    roll: DiceRoll,
    succeeded: bool,
    target_number: int,
    roller: EncounterCombatant,
    setup: EncounterSetup | None,
    dice: DiceProvider,
    *,
    outcome_locked: bool = False,
) -> tuple[DiceRoll, bool, str | None]:
    """Apply one deterministic post-result D20 adjustment when it can reverse the outcome."""
    try:
        if setup is None or outcome_locked:
            return roll, succeeded, None
        for source in _candidate_sources(roller, setup, succeeded):
            rule = source.state.template.progression_features.d20_outcome_adjustment
            if rule is None:
                continue
            gap = _reversal_gap(roll.total, target_number, succeeded)
            if gap <= 0 or gap > rule.dice_count * rule.dice_size:
                continue
            adjustment_rolls = [dice.roll(rule.dice_size) for _ in range(rule.dice_count)]
            sign = -1 if succeeded else 1
            replacement_total = roll.total + sign * sum(adjustment_rolls)
            spend_resource(source.state, rule.resource_id)
            revision = RollRevision(
                source_effect_id=rule.source_id,
                kind="total_adjustment",
                original_rolls=list(roll.rolls),
                replacement_rolls=list(roll.rolls),
                original_modifier=roll.modifier,
                replacement_modifier=roll.modifier,
                original_selected=roll.selected_roll,
                replacement_selected=roll.selected_roll,
                original_total=roll.total,
                replacement_total=replacement_total,
                accepted="replacement",
                adjustment_rolls=adjustment_rolls,
                adjustment_sign=sign,
            )
            notation = f"{roll.notation} [{rule.source_id} {sign:+d}{rule.dice_count}d{rule.dice_size}]"
            updated = roll.model_copy(update={
                "notation": notation,
                "total": replacement_total,
                "revisions": [*roll.revisions, revision],
            })
            return updated, replacement_total >= target_number, source.combatant_id
        return roll, succeeded, None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "D20 outcome adjustment failed for roller=%s target=%s.",
            roller.combatant_id,
            target_number,
        )
        raise RuntimeError("D20 outcome adjustment could not be resolved.") from exc
