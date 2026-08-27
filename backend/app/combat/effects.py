from __future__ import annotations

import logging

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
            if effect.effect_type != "push":
                raise ValueError(f"Unsupported attack effect: {effect.effect_type}")

            before = battlefield.distance_ft
            battlefield.distance_ft += effect.distance_ft
            events.append(BattleEvent(
                sequence=sequence + len(events),
                round_number=round_number,
                event_type="forced_movement",
                actor_id=attacker.template.id,
                actor_name=attacker.template.name,
                target_id=defender.template.id,
                target_name=defender.template.name,
                distance_before_ft=before,
                distance_after_ft=battlefield.distance_ft,
                movement_ft=effect.distance_ft,
                feature_id=effect.id,
                animation="push",
                description=(
                    f"{attacker.template.name} pushes {defender.template.name} "
                    f"{effect.distance_ft} ft."
                ),
            ))
        return events
    except Exception as exc:
        logger.exception("On-hit effect resolution failed for %s.", attack.id)
        raise RuntimeError("On-hit effects could not be resolved.") from exc
