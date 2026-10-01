from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.damage_reaction_wrappers import resolve_attack_event_chain
from app.combat.pit_policy import choose_attack
from app.combat.resources import action_resource_available, spend_action_resource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_bonus_attack_grant(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve the highest-priority legal declarative Bonus Action attack grant."""
    try:
        state = attacker.state
        if state.turn_terminated or not is_available(state, "bonus_action"):
            return [], sequence
        grants = sorted(state.template.bonus_attack_grants, key=lambda item: (item.priority, item.id))
        for grant in grants:
            if not action_resource_available(state, grant):
                continue
            choice = choose_attack(attacker, setup, grant.attack_ids)
            if choice is None:
                continue

            spend(state, "bonus_action")
            spend_action_resource(state, grant)
            events: list[BattleEvent] = []
            for strike_index in range(grant.attack_count):
                if state.turn_terminated:
                    break
                current = choice if strike_index == 0 else choose_attack(attacker, setup, grant.attack_ids)
                if current is None:
                    break
                target, attack, distance = current
                if grant.on_hit_condition_save is not None:
                    attack = attack.model_copy(update={"on_hit_condition_save": grant.on_hit_condition_save})
                pack = pack_tactics_active(attacker, target, setup)
                strike_events, sequence = resolve_attack_event_chain(
                    sequence,
                    round_number,
                    attacker,
                    target,
                    attack,
                    distance,
                    dice,
                    setup,
                    spend_action=False,
                    advantage_sources=1 if pack else 0,
                    feature_id=grant.id,
                    turn_key=turn_key,
                    allow_reckless=True,
                    close_enemy_active=False,
                )
                events.extend(strike_events)
            return events, sequence
        return [], sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Bonus attack grant resolution failed for %s.", attacker.combatant_id)
        raise RuntimeError("Bonus attack grant could not be resolved.") from exc
