from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.resources import resource_state
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def delayed_resource_refill_rule(actor: EncounterCombatant):
    try:
        return actor.state.template.progression_features.delayed_resource_refill
    except Exception:
        logger.exception("Failed delayed-refill rule lookup for %s.", actor.combatant_id)
        raise RuntimeError("Committed resource activity rule could not be read.") from None


def active_refill_timer(actor: EncounterCombatant, rule):
    try:
        return next(
            (item for item in actor.state.delayed_resource_refills if item.source_id == rule.source_id),
            None,
        )
    except Exception:
        logger.exception("Failed delayed-refill timer lookup for %s.", actor.combatant_id)
        raise RuntimeError("Committed resource activity timer could not be read.") from None


def _clear_timer(actor: EncounterCombatant, timer) -> None:
    actor.state.delayed_resource_refills = [
        item for item in actor.state.delayed_resource_refills if item is not timer
    ]


def _restore_resources(actor: EncounterCombatant, rule) -> list[str]:
    restored: list[str] = []
    for resource_id in rule.resource_ids:
        resource = resource_state(actor.state, resource_id)
        if resource is None:
            raise ValueError(f"{rule.source_name} references missing resource {resource_id}.")
        if resource.current_uses >= resource.max_uses:
            continue
        if rule.restore_mode == "half_max_rounded_up":
            regain = (resource.max_uses + 1) // 2
            resource.current_uses = min(resource.max_uses, resource.current_uses + regain)
        else:
            resource.current_uses = resource.max_uses
        restored.append(resource_id)
    return restored


def resolve_delayed_resource_refill_end_turn(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    """Complete or cancel an already-started committed refill. Never auto-start one."""
    try:
        rule = delayed_resource_refill_rule(actor)
        if rule is None:
            return [], sequence
        timer = active_refill_timer(actor, rule)
        if timer is None:
            return [], sequence
        name = actor.state.template.name
        if actor.state.is_dead or is_incapacitated(actor.state):
            _clear_timer(actor, timer)
            event = BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=actor.combatant_id,
                actor_name=name,
                target_id=actor.combatant_id,
                target_name=name,
                feature_id=rule.source_id,
                animation="resource-refill",
                description=(
                    f"{name} stops {rule.source_name} before it completes and restores no resources."
                ),
            )
            return [event], sequence + 1
        if round_number < timer.completes_round:
            return [], sequence
        restored = _restore_resources(actor, rule)
        _clear_timer(actor, timer)
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=name,
            target_id=actor.combatant_id,
            target_name=name,
            feature_id=rule.source_id,
            animation="resource-refill",
            description=(
                f"{name} completes {rule.source_name} and restores "
                f"{', '.join(restored) if restored else 'no depleted resources'}."
            ),
        )
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Delayed resource refill failed for %s.", actor.combatant_id)
        raise RuntimeError("Delayed resource refill could not be resolved.") from exc
