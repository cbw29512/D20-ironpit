from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.effects import resolve_on_hit_effects
from app.combat.multiattack_policy import select_multiattack_weapon, select_save_replacement
from app.combat.save_actions import resolve_save_action
from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)


def resolve_multiattack_action(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    target: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    visible_source_ids: set[str] | None = None,
) -> list[BattleEvent]:
    try:
        routine = actor.template.multiattack
        if routine is None:
            raise ValueError(f"{actor.template.name} has no Multiattack action.")
        if not actor.action_available:
            raise ValueError("Action is not available for Multiattack.")

        actor.action_available = False
        events: list[BattleEvent] = []
        replacements_used = 0
        for _ in range(routine.attack_count):
            if not target.is_alive:
                break
            replacement = select_save_replacement(
                actor, target, routine, battlefield.distance_ft, replacements_used
            )
            if replacement is not None:
                replacement_events = resolve_save_action(
                    sequence + len(events),
                    round_number,
                    actor,
                    target,
                    battlefield.distance_ft,
                    replacement,
                    dice,
                    spend_action_cost=False,
                )
                events.extend(replacement_events)
                replacements_used += 1
                continue

            attack = select_multiattack_weapon(actor, routine, battlefield.distance_ft)
            if attack is None:
                break
            attack_event = resolve_attack(
                sequence + len(events),
                round_number,
                actor,
                target,
                attack,
                battlefield.distance_ft,
                dice,
                visible_source_ids,
            )
            events.append(attack_event)
            events.extend(resolve_on_hit_effects(
                sequence + len(events),
                round_number,
                actor,
                target,
                attack,
                battlefield,
                attack_event,
                dice,
            ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Multiattack failed: %s -> %s.", actor.template.name, target.template.name)
        raise RuntimeError("Multiattack could not be resolved.") from exc
