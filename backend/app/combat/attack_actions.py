from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.effects import resolve_on_hit_effects
from app.combat.policy import select_weapon_attack
from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)


def resolve_attack_action(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    visible_source_ids: set[str] | None = None,
) -> list[BattleEvent]:
    """Spend one Attack action, rechecking legal attack profiles after every strike."""
    try:
        if not attacker.action_available:
            raise ValueError("Action is not available for an attack.")

        attacker.action_available = False
        events: list[BattleEvent] = []
        for _ in range(attacker.template.attacks_per_action):
            if not defender.is_alive:
                break

            attack = select_weapon_attack(attacker, battlefield.distance_ft)
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
            ))
        return events
    except Exception as exc:
        logger.exception("Attack action failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack action could not be resolved.") from exc
