from __future__ import annotations

import logging

from app.combat.counterattack_planning import counterattack_plan
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)
_MAX_REACTION_DEPTH = 8


def resolve_attack_event_chain(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    setup: EncounterSetup,
    *,
    reaction_depth: int = 0,
    **attack_options,
) -> tuple[list[BattleEvent], int]:
    """Resolve one attack and any immediate AC-conversion counterattack chain."""
    try:
        if reaction_depth > _MAX_REACTION_DEPTH:
            raise RuntimeError("Maximum immediate reaction depth exceeded.")
        turn_owner_id = attack_options.get("turn_owner_id")
        if turn_owner_id is None and not attack_options.get("off_turn", False):
            turn_owner_id = attacker.combatant_id
        event = resolve_encounter_attack(
            sequence, round_number, attacker, target, attack, distance_ft,
            dice, setup, **{**attack_options, "turn_owner_id": turn_owner_id},
        )
        events = [event]
        sequence += 1
        planned = counterattack_plan(event, attacker, setup)
        if planned is None:
            return events, sequence

        reactor, counter, counter_distance = planned
        rule = reactor.state.template.parry_reaction
        if rule is None:
            raise RuntimeError("Counterattack reaction state disappeared.")
        more, sequence = resolve_attack_event_chain(
            sequence, round_number, reactor, attacker, counter,
            counter_distance, dice, setup,
            reaction_depth=reaction_depth + 1,
            spend_action=False,
            feature_id=rule.source_feature,
            turn_key=attack_options.get("turn_key"),
            close_enemy_active=True,
            allow_reckless=False,
            off_turn=True,
            turn_owner_id=turn_owner_id,
        )
        events.extend(more)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Attack reaction chain failed: attacker=%s target=%s attack=%s.",
            attacker.combatant_id, target.combatant_id, attack.id,
        )
        raise RuntimeError("Attack reaction chain could not be resolved.") from exc
