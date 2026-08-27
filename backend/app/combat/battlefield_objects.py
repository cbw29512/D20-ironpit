from __future__ import annotations

import logging

from app.combat.conditions import has_condition, remove_condition_instance
from app.domain.models import (
    BattleEvent,
    BattlefieldObjectDefinition,
    BattlefieldObjectState,
    BattlefieldState,
    CombatantState,
    DamageType,
)

logger = logging.getLogger(__name__)


def create_battlefield_object(
    battlefield: BattlefieldState,
    definition: BattlefieldObjectDefinition,
    instance_id: str,
    source: CombatantState,
    target: CombatantState | None = None,
    linked_condition=None,
) -> BattlefieldObjectState:
    if any(item.instance_id == instance_id for item in battlefield.objects):
        raise ValueError(f"Battlefield object already exists: {instance_id}")
    state = BattlefieldObjectState(
        instance_id=instance_id,
        definition=definition,
        source_id=source.instance_id,
        target_id=target.instance_id if target else None,
        linked_condition=linked_condition,
        current_hp=definition.max_hp,
    )
    battlefield.objects.append(state)
    return state


def get_battlefield_object(
    battlefield: BattlefieldState,
    object_id: str,
) -> BattlefieldObjectState:
    state = next((item for item in battlefield.objects if item.instance_id == object_id), None)
    if state is None:
        raise ValueError(f"Unknown battlefield object: {object_id}")
    return state


def _apply_damage_rules(
    state: BattlefieldObjectState,
    amount: int,
    damage_type: DamageType,
) -> int:
    if damage_type in state.definition.damage_immunities:
        return 0
    if damage_type in state.definition.damage_vulnerabilities:
        return amount * 2
    return amount


def damage_battlefield_object(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    battlefield: BattlefieldState,
    object_id: str,
    damage_type: DamageType,
    amount: int,
    combatants: list[CombatantState],
) -> list[BattleEvent]:
    try:
        if amount < 0:
            raise ValueError("Object damage cannot be negative.")
        state = get_battlefield_object(battlefield, object_id)
        if state.is_destroyed:
            raise ValueError(f"Battlefield object is already destroyed: {object_id}")

        before = state.current_hp
        applied = _apply_damage_rules(state, amount, damage_type)
        state.current_hp = max(0, state.current_hp - applied)
        events = [BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="object_damage",
            actor_id=actor.instance_id,
            actor_name=actor.template.name,
            object_id=state.instance_id,
            object_name=state.definition.name,
            damage_applied=applied,
            hp_before=before,
            hp_after=state.current_hp,
            animation="object-damage",
            description=(
                f"{state.definition.name} takes {applied} {damage_type.value} damage."
            ),
        )]
        if state.current_hp > 0:
            return events

        state.is_destroyed = True
        events.append(BattleEvent(
            sequence=sequence + len(events),
            round_number=round_number,
            event_type="object_destroyed",
            actor_id=actor.instance_id,
            actor_name=actor.template.name,
            object_id=state.instance_id,
            object_name=state.definition.name,
            animation="object-destroyed",
            description=f"{state.definition.name} is destroyed.",
        ))
        if state.target_id is None or state.linked_condition is None:
            return events

        target = next((item for item in combatants if item.instance_id == state.target_id), None)
        if target is None:
            raise ValueError(f"Object target is missing: {state.target_id}")
        if not remove_condition_instance(
            target,
            state.linked_condition,
            linked_object_id=state.instance_id,
        ):
            return events
        events.append(BattleEvent(
            sequence=sequence + len(events),
            round_number=round_number,
            event_type="condition",
            actor_id=target.instance_id,
            actor_name=target.template.name,
            target_id=target.instance_id,
            target_name=target.template.name,
            object_id=state.instance_id,
            condition=state.linked_condition,
            condition_active=has_condition(target, state.linked_condition),
            feature_id="object-destruction",
            animation="condition-end",
            description=(
                f"{target.template.name}'s {state.linked_condition.value.title()} source ends."
            ),
        ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Battlefield object damage failed for %s.", object_id)
        raise RuntimeError("Battlefield object damage could not be resolved.") from exc
