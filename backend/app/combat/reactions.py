from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.policy import attack_uses_melee
from app.domain.models import BattleEvent, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def select_opportunity_attack(
    reactor: CombatantState,
    distance_before_ft: int,
    distance_after_ft: int,
) -> WeaponAttack | None:
    """Choose an explicit melee-capable attack whose reach is being left."""
    profiles = [reactor.template.weapon_attack, *reactor.template.alternate_weapon_attacks]
    for attack in profiles:
        reach = attack.weapon.reach_ft
        if (
            distance_before_ft <= reach
            and distance_after_ft > reach
            and attack_uses_melee(attack, distance_before_ft)
        ):
            return attack
    return None


def resolve_opportunity_attack(
    sequence: int,
    round_number: int,
    reactor: CombatantState,
    mover: CombatantState,
    distance_before_ft: int,
    distance_after_ft: int,
    dice: DiceProvider,
    *,
    mover_visible: bool = True,
    movement_uses_mover_economy: bool = True,
    teleport: bool = False,
) -> BattleEvent | None:
    """Resolve a weapon Opportunity Attack immediately before the mover leaves reach."""
    try:
        if not reactor.is_alive or not mover.is_alive:
            return None
        if not reactor.reaction_available or not mover_visible:
            return None
        if mover.disengaged_this_turn or teleport or not movement_uses_mover_economy:
            return None

        attack = select_opportunity_attack(
            reactor,
            distance_before_ft,
            distance_after_ft,
        )
        if attack is None:
            return None

        reactor.reaction_available = False
        return resolve_attack(
            sequence,
            round_number,
            reactor,
            mover,
            attack,
            distance_before_ft,
            dice,
            visible_source_ids={mover.instance_id},
            event_type="opportunity_attack",
        )
    except Exception as exc:
        logger.exception(
            "Opportunity Attack failed: %s -> %s.",
            reactor.template.name,
            mover.template.name,
        )
        raise RuntimeError("Opportunity Attack could not be resolved.") from exc
