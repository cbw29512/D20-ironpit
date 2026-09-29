from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.encounter_targeting import combatant_distance
from app.combat.dice import DiceProvider
from app.combat.resources import resource_available, spend_resource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.event_support import DiceRoll, RollRevision
from app.domain.progression_primitives import ResourceBackedD20OutcomeAdjustment

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class D20OutcomeAdjustmentResult:
    roll: DiceRoll
    source_id: str
    source_name: str
    adjustment_total: int
    direction: str
    resource_remaining: int


def _resources(source: EncounterCombatant):
    return {item.id: item for item in source.state.resources}


def _eligible(
    source: EncounterCombatant,
    roller: EncounterCombatant,
    rule: ResourceBackedD20OutcomeAdjustment,
    test_kind: str,
) -> bool:
    if source.state.is_dead or not source.state.is_alive:
        return False
    if test_kind not in rule.test_kinds:
        return False
    if not resource_available(source.state, rule.resource_id, rule.resource_cost):
        return False
    return combatant_distance(source, roller) <= rule.range_ft


def _direction(
    source: EncounterCombatant,
    roller: EncounterCombatant,
    rule: ResourceBackedD20OutcomeAdjustment,
    roll: DiceRoll,
    target_total: int,
) -> str | None:
    maximum = rule.dice_count * rule.dice_size
    allied = source.side == roller.side
    if allied and rule.can_add and roll.total < target_total and roll.total + maximum >= target_total:
        return "add"
    if not allied and rule.can_subtract and roll.total >= target_total and roll.total - maximum < target_total:
        return "subtract"
    return None


def apply_resource_backed_d20_outcome_adjustment_if_useful(
    roller: EncounterCombatant,
    setup: EncounterSetup,
    test_kind: str,
    roll: DiceRoll,
    target_total: int,
    dice: DiceProvider,
    *,
    natural_attack_roll: int | None = None,
) -> D20OutcomeAdjustmentResult | None:
    """Apply one deterministic source-neutral adjustment that could change a D20 Test outcome."""
    try:
        if test_kind == "attack" and natural_attack_roll in {1, 20}:
            return None

        choices: list[tuple[EncounterCombatant, ResourceBackedD20OutcomeAdjustment, str]] = []
        for source in [*setup.heroes, *setup.monsters]:
            for rule in source.state.template.progression_features.resource_backed_d20_outcome_adjustments:
                if not _eligible(source, roller, rule, test_kind):
                    continue
                direction = _direction(source, roller, rule, roll, target_total)
                if direction is not None:
                    choices.append((source, rule, direction))
        if not choices:
            return None

        source, rule, direction = max(
            choices,
            key=lambda item: (
                item[1].dice_count * item[1].dice_size,
                -combatant_distance(item[0], roller),
                item[0].combatant_id,
                item[1].source_id,
            ),
        )
        adjustment_rolls = [dice.roll(rule.dice_size) for _ in range(rule.dice_count)]
        adjustment = sum(adjustment_rolls)
        signed = adjustment if direction == "add" else -adjustment
        replacement_total = roll.total + signed
        spend_resource(source.state, rule.resource_id, rule.resource_cost)
        resource = _resources(source)[rule.resource_id]

        revision = RollRevision(
            source_effect_id=rule.source_id,
            kind="roll_adjustment",
            original_rolls=list(roll.rolls),
            replacement_rolls=[*roll.rolls, *adjustment_rolls],
            original_modifier=roll.modifier,
            replacement_modifier=roll.modifier + signed,
            original_selected=roll.selected_roll,
            replacement_selected=roll.selected_roll,
            original_total=roll.total,
            replacement_total=replacement_total,
            accepted="replacement",
        )
        operator = "+" if direction == "add" else "-"
        revised = roll.model_copy(update={
            "notation": (
                f"{roll.notation} {operator} {rule.dice_count}d{rule.dice_size} "
                f"[{rule.source_name}]"
            ),
            "rolls": [*roll.rolls, *adjustment_rolls],
            "modifier": roll.modifier + signed,
            "total": replacement_total,
            "revisions": [*roll.revisions, revision],
        })
        return D20OutcomeAdjustmentResult(
            roll=revised,
            source_id=rule.source_id,
            source_name=rule.source_name,
            adjustment_total=adjustment,
            direction=direction,
            resource_remaining=resource.current_uses,
        )
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("D20 outcome adjustment failed for %s.", roller.combatant_id)
        raise RuntimeError("D20 outcome adjustment could not be resolved.") from exc
