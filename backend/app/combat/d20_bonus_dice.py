from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.d20_bonus_die_support import grant_conflicts, resource_for, target_allowed
from app.combat.dice import DiceProvider
from app.domain.d20_bonus_dice import ActiveD20BonusDieGrant, D20BonusDieAction, D20TestKind
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent, DiceRoll

logger = logging.getLogger(__name__)


def resolve_d20_bonus_die_grant(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    target: EncounterCombatant,
    action: D20BonusDieAction,
) -> BattleEvent:
    """Spend the declared action/resource and attach one fresh finite-duration grant."""
    try:
        if not is_available(source.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        resource = resource_for(source, action)
        if resource is None or resource.current_uses < action.resource_cost:
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        if not target_allowed(source, target, action):
            raise ValueError(f"{target.state.template.name} is not a legal target for {action.name}.")
        expire_d20_bonus_dice(target.state, round_number)
        if grant_conflicts(source, target, action, round_number):
            raise ValueError(f"{target.state.template.name} already has an exclusive {action.name} grant.")

        spend(source.state, action.action_cost)
        resource.current_uses -= action.resource_cost
        target.state.active_d20_bonus_dice.append(ActiveD20BonusDieGrant(
            source_id=source.combatant_id,
            source_effect_id=action.id,
            source_name=action.name,
            dice_count=action.dice_count,
            dice_size=action.dice_size,
            test_kinds=list(action.test_kinds),
            exclusive_group=action.exclusive_group,
            applied_round=round_number,
            expires_round=round_number + action.duration_rounds,
        ))
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=source.combatant_id,
            actor_name=source.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            feature_id=action.id,
            resource_remaining=resource.current_uses,
            animation=action.animation,
            description=(
                f"{source.state.template.name} grants {action.name} to "
                f"{target.state.template.name}."
            ),
        )
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Failed to grant %s from %s.", action.name, source.combatant_id)
        raise RuntimeError("D20 bonus-die grant could not be resolved.") from exc


def eligible_d20_bonus_dice(
    state,
    test_kind: D20TestKind,
    round_number: int,
) -> list[ActiveD20BonusDieGrant]:
    try:
        expire_d20_bonus_dice(state, round_number)
        return [
            item for item in state.active_d20_bonus_dice
            if test_kind in item.test_kinds and item.expires_round > round_number
        ]
    except Exception as exc:
        logger.exception("Failed to identify eligible d20 bonus dice for %s.", state.template.name)
        raise RuntimeError("D20 bonus-die eligibility could not be resolved.") from exc


def consume_d20_bonus_die(
    state,
    grant: ActiveD20BonusDieGrant,
    roll: DiceRoll,
    dice: DiceProvider,
) -> DiceRoll:
    """Roll and consume one already-selected d20 bonus-die grant."""
    try:
        if grant not in state.active_d20_bonus_dice:
            raise ValueError("Selected d20 bonus-die grant is not active.")
        bonus_rolls = [dice.roll(grant.dice_size) for _ in range(grant.dice_count)]
        state.active_d20_bonus_dice.remove(grant)
        return roll.model_copy(update={
            "notation": f"{roll.notation} + {grant.dice_count}d{grant.dice_size} [{grant.source_name}]",
            "rolls": [*roll.rolls, *bonus_rolls],
            "total": roll.total + sum(bonus_rolls),
        })
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to consume d20 bonus die for %s.", state.template.name)
        raise RuntimeError("D20 bonus die could not be consumed.") from exc


def apply_d20_bonus_die_if_useful(
    state,
    test_kind: D20TestKind,
    roll: DiceRoll,
    target_total: int,
    dice: DiceProvider,
    round_number: int,
) -> tuple[DiceRoll, str | None]:
    """Choose before rolling the bonus die and spend it only on a potentially recoverable failed test."""
    try:
        if roll.total >= target_total:
            return roll, None
        grants = eligible_d20_bonus_dice(state, test_kind, round_number)
        useful = [
            grant for grant in grants
            if roll.total + grant.dice_count * grant.dice_size >= target_total
        ]
        if not useful:
            return roll, None
        grant = max(useful, key=lambda item: (item.dice_count * item.dice_size, item.source_effect_id))
        return consume_d20_bonus_die(state, grant, roll, dice), grant.source_name
    except Exception as exc:
        logger.exception("Failed to apply d20 bonus die for %s.", state.template.name)
        raise RuntimeError("D20 bonus die could not be applied to the test.") from exc


def expire_d20_bonus_dice(state, round_number: int) -> list[str]:
    """Expire grants whose absolute round lifetime has ended."""
    try:
        expired = [
            item.source_effect_id
            for item in state.active_d20_bonus_dice
            if item.expires_round <= round_number
        ]
        state.active_d20_bonus_dice = [
            item for item in state.active_d20_bonus_dice
            if item.expires_round > round_number
        ]
        return expired
    except Exception as exc:
        logger.exception("Failed to expire d20 bonus dice for %s.", state.template.name)
        raise RuntimeError("D20 bonus-die expiry could not be resolved.") from exc
