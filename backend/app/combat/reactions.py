from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.conditions import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.movement import move_away_from_target
from app.combat.sight import can_see_combatant
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, WeaponAttackKind

logger = logging.getLogger(__name__)
OPPORTUNITY_ATTACK = "opportunity-attack"


def _select_melee_reaction_attack(
    reactor: CombatantState,
    distance_ft: int,
):
    try:
        profiles = [reactor.template.weapon_attack, *reactor.template.alternate_weapon_attacks]
        return next(
            (
                attack for attack in profiles
                if attack.weapon.attack_kind is WeaponAttackKind.MELEE
                and distance_ft <= attack.weapon.reach_ft
            ),
            None,
        )
    except Exception as exc:
        logger.exception("Failed to select reaction attack for %s.", reactor.template.name)
        raise RuntimeError("Reaction attack selection failed.") from exc


def resolve_opportunity_attack(
    sequence: int,
    round_number: int,
    reactor: CombatantState,
    mover: CombatantState,
    distance_before_ft: int,
    distance_after_ft: int,
    dice: DiceProvider,
    battlefield: BattlefieldState | None = None,
) -> BattleEvent | None:
    try:
        if (
            mover.disengaged
            or not reactor.reaction_available
            or not reactor.is_alive
            or is_incapacitated(reactor)
        ):
            return None
        if not can_see_combatant(reactor, mover, battlefield):
            return None
        attack = _select_melee_reaction_attack(reactor, distance_before_ft)
        if attack is None or distance_after_ft <= attack.weapon.reach_ft:
            return None

        reactor.reaction_available = False
        event = resolve_attack(
            sequence,
            round_number,
            reactor,
            mover,
            attack,
            distance_before_ft,
            dice,
            spend_action=False,
            battlefield=battlefield,
        )
        event.reaction_id = OPPORTUNITY_ATTACK
        event.description = f"Opportunity Attack — {event.description}"
        return event
    except Exception as exc:
        logger.exception("Opportunity Attack failed: %s -> %s.", reactor.template.name, mover.template.name)
        raise RuntimeError("Opportunity Attack could not be resolved.") from exc


def retreat_with_opportunity_check(
    sequence: int,
    round_number: int,
    mover: CombatantState,
    reactor: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        moved = mover.movement_remaining_ft
        if moved <= 0:
            return events, sequence
        before = battlefield.distance_ft
        reaction = resolve_opportunity_attack(
            sequence,
            round_number,
            reactor,
            mover,
            before,
            before + moved,
            dice,
            battlefield=battlefield,
        )
        if reaction is not None:
            events.append(reaction)
            sequence += 1
            if not mover.is_alive:
                return events, sequence

        movement = move_away_from_target(sequence, round_number, mover, battlefield)
        if movement is not None:
            events.append(movement)
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Retreat reaction check failed for %s.", mover.template.name)
        raise RuntimeError("Retreat could not be resolved.") from exc
