from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
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
) -> list[BattleEvent]:
    """Spend one Attack action and resolve the combatant's allowed attack count."""
    try:
        if not attacker.action_available:
            raise ValueError("Action is not available for an attack.")

        attacker.action_available = False
        events: list[BattleEvent] = []
        for offset in range(attacker.template.attacks_per_action):
            if not defender.is_alive:
                break
            events.append(
                resolve_attack(
                    sequence + offset,
                    round_number,
                    attacker,
                    defender,
                    attack,
                    distance_ft,
                    dice,
                )
            )
        return events
    except Exception as exc:
        logger.exception("Attack action failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack action could not be resolved.") from exc
