from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.condition_modifiers import is_incapacitated
from app.combat.effects import resolve_on_hit_effects
from app.combat.policy import attack_uses_melee
from app.combat.range import resolve_attack_roll_mode
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def _opportunity_weapon(
    reactor: CombatantState,
    distance_before_ft: int,
    distance_after_ft: int,
) -> WeaponAttack | None:
    profiles = [reactor.template.weapon_attack, *reactor.template.alternate_weapon_attacks]
    for attack in profiles:
        reach = attack.weapon.reach_ft
        if not (distance_before_ft <= reach < distance_after_ft):
            continue
        if not attack_uses_melee(attack, distance_before_ft):
            continue
        try:
            resolve_attack_roll_mode(attack.weapon, distance_before_ft)
            return attack
        except ValueError:
            continue
    return None


def resolve_opportunity_attack(
    sequence: int,
    round_number: int,
    reactor: CombatantState,
    mover: CombatantState,
    battlefield: BattlefieldState,
    intended_distance_after_ft: int,
    dice,
    mover_visible: bool = True,
) -> list[BattleEvent]:
    """Resolve one weapon OA immediately before a visible mover leaves weapon reach."""
    try:
        if not mover_visible or mover.disengaged_this_turn:
            return []
        if not reactor.reaction_available or is_incapacitated(reactor):
            return []
        if not reactor.is_alive or not mover.is_alive:
            return []

        attack = _opportunity_weapon(
            reactor,
            battlefield.distance_ft,
            intended_distance_after_ft,
        )
        if attack is None:
            return []

        reactor.reaction_available = False
        attack_event = resolve_attack(
            sequence,
            round_number,
            reactor,
            mover,
            attack,
            battlefield.distance_ft,
            dice,
            {mover.instance_id},
        )
        attack_event.feature_id = "opportunity-attack"
        attack_event.description = (
            f"{reactor.template.name} makes an Opportunity Attack: "
            f"{attack_event.description}"
        )
        events = [attack_event]
        events.extend(resolve_on_hit_effects(
            sequence + 1,
            round_number,
            reactor,
            mover,
            attack,
            battlefield,
            attack_event,
            dice,
        ))
        return events
    except Exception as exc:
        logger.exception(
            "Opportunity Attack failed: %s -> %s.",
            reactor.template.name,
            mover.template.name,
        )
        raise RuntimeError("Opportunity Attack could not be resolved.") from exc
