from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.effects import resolve_on_hit_effects
from app.combat.multiattack_policy import select_multiattack_weapon
from app.combat.object_attacks import resolve_object_attack
from app.combat.policy import select_weapon_attack
from app.domain.models import (
    BattleEvent,
    BattlefieldObjectState,
    BattlefieldState,
    CombatantState,
    WeaponAttack,
)

logger = logging.getLogger(__name__)


def select_linked_object(
    attacker: CombatantState,
    battlefield: BattlefieldState,
) -> BattlefieldObjectState | None:
    """Return the first live object currently linked to one of the attacker's conditions."""
    try:
        linked_ids = {
            item.linked_object_id
            for item in attacker.conditions
            if item.linked_object_id is not None
        }
        return next(
            (
                obj for obj in battlefield.objects
                if obj.instance_id in linked_ids
                and obj.target_id == attacker.instance_id
                and not obj.is_destroyed
            ),
            None,
        )
    except Exception as exc:
        logger.exception("Linked object selection failed for %s.", attacker.template.name)
        raise RuntimeError("Linked battlefield object could not be selected.") from exc


def _select_attack(
    attacker: CombatantState,
    distance_ft: int,
) -> WeaponAttack | None:
    routine = attacker.template.multiattack
    if routine is not None:
        return select_multiattack_weapon(attacker, routine, distance_ft)
    return select_weapon_attack(attacker, distance_ft)


def _attack_count(attacker: CombatantState) -> int:
    routine = attacker.template.multiattack
    return routine.attack_count if routine is not None else attacker.template.attacks_per_action


def resolve_object_priority_attack_action(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice,
    visible_source_ids: set[str] | None = None,
) -> list[BattleEvent]:
    """Spend an attack-based Action breaking linked objects before attacking the enemy."""
    try:
        if not attacker.action_available:
            raise ValueError("Action is not available for an attack.")
        if select_linked_object(attacker, battlefield) is None:
            raise ValueError("No live linked battlefield object requires an attack.")

        attacker.action_available = False
        events: list[BattleEvent] = []
        roster = [attacker, defender]
        for _ in range(_attack_count(attacker)):
            linked = select_linked_object(attacker, battlefield)
            if linked is not None:
                attack = _select_attack(attacker, 0)
                if attack is None:
                    break
                events.extend(resolve_object_attack(
                    sequence + len(events),
                    round_number,
                    attacker,
                    battlefield,
                    linked.instance_id,
                    attack,
                    dice,
                    roster,
                    visible_source_ids,
                ))
                continue

            if not defender.is_alive:
                break
            attack = _select_attack(attacker, battlefield.distance_ft)
            if attack is None:
                break
            attack_event = resolve_attack(
                sequence + len(events),
                round_number,
                attacker,
                defender,
                attack,
                battlefield.distance_ft,
                dice,
                visible_source_ids,
            )
            events.append(attack_event)
            events.extend(resolve_on_hit_effects(
                sequence + len(events),
                round_number,
                attacker,
                defender,
                attack,
                battlefield,
                attack_event,
                dice,
            ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Object-priority Attack action failed for %s.", attacker.template.name)
        raise RuntimeError("Object-priority Attack action could not be resolved.") from exc
