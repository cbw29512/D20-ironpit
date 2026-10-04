from __future__ import annotations

import logging

from app.combat.resources import resource_state, spend_resource
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.runtime import DelayedResourceRefillState

logger = logging.getLogger(__name__)


def resolve_delayed_resource_refill_end_turn(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    """Arm or complete one source-owned delayed resource refill at source turn end."""
    try:
        rule = actor.state.template.progression_features.delayed_resource_refill
        if rule is None:
            return [], sequence

        timer = next(
            (item for item in actor.state.delayed_resource_refills if item.source_id == rule.source_id),
            None,
        )
        if timer is not None:
            if round_number < timer.completes_round:
                return [], sequence
            restored: list[str] = []
            for resource_id in rule.resource_ids:
                resource = resource_state(actor.state, resource_id)
                if resource is None:
                    raise ValueError(f"{rule.source_name} references missing resource {resource_id}.")
                if resource.current_uses < resource.max_uses:
                    if rule.restore_mode == "half_max_rounded_up":
                        regain = (resource.max_uses + 1) // 2
                        resource.current_uses = min(
                            resource.max_uses,
                            resource.current_uses + regain,
                        )
                    else:
                        resource.current_uses = resource.max_uses
                    restored.append(resource_id)
            actor.state.delayed_resource_refills = [
                item for item in actor.state.delayed_resource_refills if item is not timer
            ]
            event = BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=actor.combatant_id,
                actor_name=actor.state.template.name,
                target_id=actor.combatant_id,
                target_name=actor.state.template.name,
                feature_id=rule.source_id,
                animation="resource-refill",
                description=(
                    f"{actor.state.template.name} completes {rule.source_name} and restores "
                    f"{', '.join(restored) if restored else 'no depleted resources'}."
                ),
            )
            return [event], sequence + 1

        use_resource = resource_state(actor.state, rule.use_resource_id)
        if use_resource is None:
            raise ValueError(f"{rule.source_name} references missing resource {rule.use_resource_id}.")
        if use_resource.current_uses < rule.use_resource_cost:
            return [], sequence

        depleted = []
        for resource_id in rule.resource_ids:
            resource = resource_state(actor.state, resource_id)
            if resource is None:
                raise ValueError(f"{rule.source_name} references missing resource {resource_id}.")
            if resource.current_uses < resource.max_uses:
                depleted.append(resource_id)
        if not depleted:
            return [], sequence

        remaining = spend_resource(actor.state, rule.use_resource_id, rule.use_resource_cost)
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
                f"{actor.state.template.name} begins {rule.source_name}; "
                f"the refill completes after {rule.delay_rounds} rounds."
            ),
        )
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Delayed resource refill failed for %s.", actor.combatant_id)
        raise RuntimeError("Delayed resource refill could not be resolved.") from exc
