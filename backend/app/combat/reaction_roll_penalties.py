from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.event_support import DiceRoll, RollRevision
from app.domain.reaction_roll_penalties import ReactionRollKind, ReactionRollPenaltyAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReactionRollPenaltyResult:
    roll: DiceRoll
    source_name: str
    action_id: str
    penalty_total: int
    resource_remaining: int


def _resource(source: EncounterCombatant, action: ReactionRollPenaltyAction):
    return next((item for item in source.state.resources if item.id == action.resource_id), None)


def _eligible(
    source: EncounterCombatant,
    roller: EncounterCombatant,
    action: ReactionRollPenaltyAction,
    roll_kind: ReactionRollKind,
) -> bool:
    if roll_kind not in action.roll_kinds or source.side == roller.side:
        return False
    if not is_available(source.state, "reaction"):
        return False
    resource = _resource(source, action)
    if resource is None or resource.current_uses < action.resource_cost:
        return False
    if combatant_distance(source, roller) > action.range_ft:
        return False
    if action.requires_source_sight and (
        has_condition(source.state, "blinded") or has_condition(roller.state, "invisible")
    ):
        return False
    if action.requires_target_hearing and has_condition(roller.state, "deafened"):
        return False
    blocked = action.blocked_target_condition_immunity
    if blocked and condition_is_immune(roller.state, blocked, source.state.template):
        return False
    return True


def _can_change_outcome(
    action: ReactionRollPenaltyAction,
    roll_kind: ReactionRollKind,
    roll: DiceRoll,
    threshold: int | None,
) -> bool:
    if roll_kind == "damage":
        return roll.total > 0
    if threshold is None or roll.total < threshold:
        return False
    if roll_kind == "attack" and roll.selected_roll in {1, 20}:
        return False
    maximum_penalty = action.dice_count * action.dice_size
    return roll.total - maximum_penalty < threshold


def choose_reaction_roll_penalty(
    roller: EncounterCombatant,
    setup: EncounterSetup,
    roll_kind: ReactionRollKind,
    roll: DiceRoll,
    *,
    threshold: int | None = None,
) -> tuple[EncounterCombatant, ReactionRollPenaltyAction] | None:
    """Choose the strongest legal hostile roll penalty that can matter to this outcome."""
    try:
        opposing = setup.monsters if roller.side == "heroes" else setup.heroes
        choices: list[tuple[EncounterCombatant, ReactionRollPenaltyAction]] = []
        for source in opposing:
            for action in source.state.template.reaction_roll_penalty_actions:
                if _eligible(source, roller, action, roll_kind) and _can_change_outcome(
                    action, roll_kind, roll, threshold,
                ):
                    choices.append((source, action))
        return max(
            choices,
            key=lambda item: (
                item[1].priority,
                item[1].dice_count * item[1].dice_size,
                -combatant_distance(item[0], roller),
                item[0].combatant_id,
                item[1].id,
            ),
            default=None,
        )
    except Exception as exc:
        logger.exception("Failed to choose reaction roll penalty against %s.", roller.combatant_id)
        raise RuntimeError("Reaction roll-penalty choice could not be resolved.") from exc


def apply_reaction_roll_penalty_if_useful(
    roller: EncounterCombatant,
    setup: EncounterSetup,
    roll_kind: ReactionRollKind,
    roll: DiceRoll,
    dice: DiceProvider,
    *,
    threshold: int | None = None,
) -> ReactionRollPenaltyResult | None:
    """Apply one selected reaction penalty and record the roll revision/resource spend."""
    try:
        choice = choose_reaction_roll_penalty(roller, setup, roll_kind, roll, threshold=threshold)
        if choice is None:
            return None
        source, action = choice
        resource = _resource(source, action)
        if resource is None:
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        penalty_rolls = [dice.roll(action.dice_size) for _ in range(action.dice_count)]
        penalty = sum(penalty_rolls)
        replacement_total = roll.total - penalty
        if roll_kind == "damage":
            replacement_total = max(0, replacement_total)
        spend(source.state, "reaction")
        resource.current_uses -= action.resource_cost
        revision = RollRevision(
            source_effect_id=action.id,
            kind="roll_penalty",
            original_rolls=list(roll.rolls),
            replacement_rolls=[*roll.rolls, *penalty_rolls],
            original_modifier=roll.modifier,
            replacement_modifier=roll.modifier - penalty,
            original_selected=roll.selected_roll,
            replacement_selected=roll.selected_roll,
            original_total=roll.total,
            replacement_total=replacement_total,
            accepted="replacement",
        )
        revised = roll.model_copy(update={
            "notation": f"{roll.notation} - {action.dice_count}d{action.dice_size} [{action.name}]",
            "rolls": [*roll.rolls, *penalty_rolls],
            "modifier": roll.modifier - penalty,
            "total": replacement_total,
            "revisions": [*roll.revisions, revision],
        })
        return ReactionRollPenaltyResult(
            roll=revised,
            source_name=source.state.template.name,
            action_id=action.id,
            penalty_total=penalty,
            resource_remaining=resource.current_uses,
        )
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Failed to apply reaction roll penalty against %s.", roller.combatant_id)
        raise RuntimeError("Reaction roll penalty could not be resolved.") from exc
