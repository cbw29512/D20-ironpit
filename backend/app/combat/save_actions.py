from __future__ import annotations

import logging

from app.combat.conditions import apply_condition
from app.combat.d20_tests import resolve_saving_throw
from app.combat.dice import DiceProvider
from app.combat.recharge import require_recharge_available, spend_recharge
from app.domain.models import BattleEvent, CombatantState, SaveAction

logger = logging.getLogger(__name__)


def _spend_action_cost(actor: CombatantState, action: SaveAction) -> None:
    if action.action_cost == "action":
        if not actor.action_available:
            raise ValueError("Action is not available for this save action.")
        actor.action_available = False
        return
    if action.action_cost == "bonus_action":
        if not actor.bonus_action_available:
            raise ValueError("Bonus Action is not available for this save action.")
        actor.bonus_action_available = False
        return
    raise ValueError(f"Unsupported save-action cost: {action.action_cost}")


def resolve_save_action(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    target: CombatantState,
    distance_ft: int,
    action: SaveAction,
    dice: DiceProvider,
    spend_action_cost: bool = True,
) -> list[BattleEvent]:
    try:
        if distance_ft > action.range_ft:
            raise ValueError(f"{action.name} target is out of range.")
        if action.target_limit != 1:
            raise ValueError("This resolver currently supports one target only.")
        if action.recharge is not None:
            require_recharge_available(actor, action.id)
        if spend_action_cost:
            _spend_action_cost(actor, action)
        if action.recharge is not None:
            spend_recharge(actor, action.id)

        roll, success = resolve_saving_throw(target, action.save_ability, action.dc, dice)
        events = [BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="saving_throw",
            actor_id=target.instance_id,
            actor_name=target.template.name,
            target_id=actor.instance_id,
            target_name=actor.template.name,
            saving_throw=roll,
            test_dc=action.dc,
            test_ability=action.save_ability,
            test_success=success,
            feature_id=action.id,
            animation=action.animation,
            description=(
                f"{target.template.name} makes a {action.save_ability.value.title()} save "
                f"against {action.name}: {'success' if success else 'failure'}."
            ),
        )]
        if success:
            return events

        for effect in action.failure_effects:
            if effect.effect_type != "condition":
                raise ValueError(f"Unsupported save failure effect: {effect.effect_type}")
            if not apply_condition(
                target,
                effect.condition,
                actor,
                expires_on=effect.expires_on,
            ):
                continue
            events.append(BattleEvent(
                sequence=sequence + len(events),
                round_number=round_number,
                event_type="condition",
                actor_id=actor.instance_id,
                actor_name=actor.template.name,
                target_id=target.instance_id,
                target_name=target.template.name,
                condition=effect.condition,
                condition_active=True,
                feature_id=action.id,
                animation="condition",
                description=(
                    f"{target.template.name} gains the {effect.condition.value.title()} condition."
                ),
            ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Save action %s failed.", action.id)
        raise RuntimeError("Save action could not be resolved.") from exc
