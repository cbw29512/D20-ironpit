from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.light_weapons import resolve_light_extra_attack
from app.domain.models import BattleEvent, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def resolve_attack_action(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve one Attack action plus any legal Light-property extra attack."""
    try:
        events = [
            resolve_attack(
                sequence,
                round_number,
                attacker,
                defender,
                attack,
                distance_ft,
                dice,
            )
        ]
        sequence += 1
        if not defender.is_alive:
            return events, sequence

        light_extra = resolve_light_extra_attack(
            sequence,
            round_number,
            attacker,
            defender,
            attack,
            distance_ft,
            dice,
        )
        if light_extra is not None:
            events.append(light_extra)
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Attack action failed for %s.", attacker.template.name)
        raise RuntimeError("Attack action could not be resolved.") from exc
