from __future__ import annotations

import logging

from app.combat.attack_effect_saves import resolve_save_condition_effect
from app.combat.conditions import apply_condition
from app.combat.dice import DiceProvider
from app.domain.models import (
    AttackEffect,
    BattleEvent,
    BattlefieldState,
    CombatantState,
    SizeCategory,
    WeaponAttack,
)

logger = logging.getLogger(__name__)
_SIZE_ORDER = list(SizeCategory)


def _effect_applies(defender: CombatantState, effect: AttackEffect) -> bool:
    if effect.max_target_size is not None:
        actual = _SIZE_ORDER.index(defender.template.size)
        maximum = _SIZE_ORDER.index(effect.max_target_size)
        if actual > maximum:
            return False
    if defender.template.creature_type in effect.excluded_creature_types:
        return False
    if set(defender.template.creature_tags) & set(effect.excluded_creature_tags):
        return False
    if effect.condition in defender.template.condition_immunities:
        return False
    return True


def resolve_on_hit_effects(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    battlefield: BattlefieldState,
    attack_event: BattleEvent,
    dice: DiceProvider,
) -> list[BattleEvent]:
    try:
        if not attack_event.hit:
            return []

        events: list[BattleEvent] = []
        for effect in attack.on_hit_effects:
            if not _effect_applies(defender, effect):
                continue
            effect_events = _resolve_effect(
                sequence + len(events),
                round_number,
                attacker,
                defender,
                battlefield,
                effect,
                dice,
            )
            events.extend(effect_events)
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
    effect: AttackEffect,
    dice: DiceProvider,
) -> list[BattleEvent]:
    if effect.effect_type == "save_condition":
        return resolve_save_condition_effect(
            sequence, round_number, attacker, defender, effect, dice
        )
    if effect.effect_type == "push":
        if effect.distance_ft is None:
            raise ValueError("Push effect is missing distance.")
        before = battlefield.distance_ft
        battlefield.distance_ft += effect.distance_ft
        return [BattleEvent(
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
        )]
    if effect.effect_type == "condition":
        if effect.condition is None or not apply_condition(
            defender,
            effect.condition,
            attacker,
            escape_dc=effect.escape_dc,
            expires_on=effect.expires_on,
        ):
            return []
        return [BattleEvent(
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
        )]
    raise ValueError(f"Unsupported attack effect: {effect.effect_type}")
