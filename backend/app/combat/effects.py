from __future__ import annotations

import logging

from app.combat.conditions import apply_condition
from app.domain.models import (
    BattleEvent,
    BattlefieldState,
    CombatantState,
    SizeCategory,
    WeaponAttack,
)

logger = logging.getLogger(__name__)
_SIZE_ORDER = list(SizeCategory)


def _size_at_most(actual: SizeCategory, maximum: SizeCategory | None) -> bool:
    return maximum is None or _SIZE_ORDER.index(actual) <= _SIZE_ORDER.index(maximum)


def resolve_on_hit_effects(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    battlefield: BattlefieldState,
    attack_event: BattleEvent,
) -> list[BattleEvent]:
    try:
        if not attack_event.hit:
            return []

        events: list[BattleEvent] = []
        for effect in attack.on_hit_effects:
            if not _size_at_most(defender.template.size, effect.max_target_size):
                continue
            event = _resolve_effect(
                sequence + len(events), round_number, attacker, defender, battlefield, effect
            )
            if event is not None:
                events.append(event)
        return events
    except Exception as exc:
        logger.exception("On-hit effect resolution failed for %s.", attack.id)
        raise RuntimeError("On-hit effects could not be resolved.") from exc


def _resolve_effect(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    effect,
) -> BattleEvent | None:
    if effect.effect_type == "push":
        if effect.distance_ft is None:
            raise ValueError("Push effect is missing distance.")
        before = battlefield.distance_ft
        battlefield.distance_ft += effect.distance_ft
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="forced_movement",
            actor_id=attacker.instance_id,
            actor_name=attacker.template.name,
            target_id=defender.instance_id,
            target_name=defender.template.name,
            distance_before_ft=before,
            distance_after_ft=battlefield.distance_ft,
            movement_ft=effect.distance_ft,
            feature_id=effect.id,
            animation="push",
            description=f"{attacker.template.name} pushes {defender.template.name} {effect.distance_ft} ft.",
        )
    if effect.effect_type == "condition":
        if effect.condition is None or not apply_condition(
            defender,
            effect.condition,
            attacker,
            escape_dc=effect.escape_dc,
        ):
            return None
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="condition",
            actor_id=attacker.instance_id,
            actor_name=attacker.template.name,
            target_id=defender.instance_id,
            target_name=defender.template.name,
            feature_id=effect.id,
            condition=effect.condition,
            condition_active=True,
            animation="condition",
            description=f"{defender.template.name} gains the {effect.condition.value.title()} condition.",
        )
    raise ValueError(f"Unsupported attack effect: {effect.effect_type}")
