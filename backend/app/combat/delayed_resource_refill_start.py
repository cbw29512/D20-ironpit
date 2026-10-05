from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.delayed_resource_refill import active_refill_timer, delayed_resource_refill_rule
from app.combat.resources import resource_state, spend_resource
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.runtime import DelayedResourceRefillState

logger = logging.getLogger(__name__)


def committed_refill_is_legal(actor: EncounterCombatant) -> bool:
    """Return whether the creature can begin its declared committed refill activity."""
    try:
        rule = delayed_resource_refill_rule(actor)
        if rule is None or active_refill_timer(actor, rule) is not None:
            return False
        if not is_available(actor.state, "action"):
            return False
        use_resource = resource_state(actor.state, rule.use_resource_id)
        if use_resource is None or use_resource.current_uses < rule.use_resource_cost:
            return False
        for resource_id in rule.resource_ids:
            resource = resource_state(actor.state, resource_id)
            if resource is None:
                raise ValueError(f"{rule.source_name} references missing resource {resource_id}.")
            if resource.current_uses < resource.max_uses:
                return True
        return False
    except ValueError:
        raise
    except Exception:
        logger.exception("Failed committed-refill legality check for %s.", actor.combatant_id)
        raise RuntimeError("Committed resource activity legality could not be checked.") from None


def start_delayed_resource_refill(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    """Spend the Action and begin performing the committed refill for its full duration."""
    try:
        rule = delayed_resource_refill_rule(actor)
        if rule is None:
            raise ValueError("No committed resource activity is declared.")
        if not committed_refill_is_legal(actor):
            raise ValueError(f"{rule.source_name} cannot begin.")
        spend(actor.state, "action")
        remaining = spend_resource(actor.state, rule.use_resource_id, rule.use_resource_cost)
        actor.state.movement_remaining_ft = 0
        actor.state.delayed_resource_refills.append(DelayedResourceRefillState(
            source_id=rule.source_id,
            started_round=round_number,
            completes_round=round_number + rule.delay_rounds,
        ))
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=actor.combatant_id,
            target_name=actor.state.template.name,
            feature_id=rule.source_id,
            resource_remaining=remaining,
            animation="resource-refill",
            description=(
                f"{actor.state.template.name} begins {rule.source_name} and spends the next "
                f"{rule.delay_rounds} rounds performing it."
            ),
        )
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Committed resource activity failed to start for %s.", actor.combatant_id)
        raise RuntimeError("Committed resource activity could not begin.") from exc
