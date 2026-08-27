from __future__ import annotations

import logging
import uuid

from app.combat.dice import DiceProvider
from app.combat.initiative import roll_initiative_order
from app.combat.state import build_combatant_state
from app.combat.turn_execution import execute_turn
from app.domain.models import BattleEvent, BattlefieldState, BattleResult, CombatantTemplate

logger = logging.getLogger(__name__)
MAX_ROUNDS = 100


def _result(
    fighter,
    monster,
    battlefield,
    events,
    rounds: int,
    winner=None,
) -> BattleResult:
    return BattleResult(
        battle_id=str(uuid.uuid4()),
        winner_id=winner.instance_id if winner else None,
        winner_name=winner.template.name if winner else None,
        rounds=rounds,
        fighter=fighter,
        monster=monster,
        battlefield=battlefield,
        events=events,
    )


def run_duel(
    fighter_template: CombatantTemplate,
    monster_template: CombatantTemplate,
    dice: DiceProvider,
    starting_distance_ft: int = 5,
) -> BattleResult:
    try:
        fighter = build_combatant_state(fighter_template)
        monster = build_combatant_state(monster_template)
        battlefield = BattlefieldState(
            starting_distance_ft=starting_distance_ft,
            distance_ft=starting_distance_ft,
        )
        events, order, sequence = roll_initiative_order(1, [fighter, monster], dice)

        for round_number in range(1, MAX_ROUNDS + 1):
            for attacker in order:
                defender = monster if attacker is fighter else fighter
                if not attacker.is_alive or not defender.is_alive:
                    continue

                turn_events, sequence = execute_turn(
                    sequence,
                    round_number,
                    attacker,
                    defender,
                    battlefield,
                    dice,
                    fighter_features=attacker is fighter,
                )
                events.extend(turn_events)

                if not defender.is_alive:
                    events.append(BattleEvent(
                        sequence=sequence,
                        round_number=round_number,
                        event_type="victory",
                        actor_id=attacker.instance_id,
                        actor_name=attacker.template.name,
                        target_id=defender.instance_id,
                        target_name=defender.template.name,
                        animation="victory",
                        description=f"{attacker.template.name} wins the duel.",
                    ))
                    return _result(
                        fighter, monster, battlefield, events, round_number, winner=attacker
                    )

        events.append(BattleEvent(
            sequence=sequence,
            round_number=MAX_ROUNDS,
            event_type="draw",
            actor_id="arena",
            actor_name="Arena",
            animation="draw",
            description=f"The duel reached the {MAX_ROUNDS}-round safety limit.",
        ))
        return _result(fighter, monster, battlefield, events, MAX_ROUNDS)
    except Exception as exc:
        logger.exception("Duel execution failed.")
        raise RuntimeError("Duel execution failed.") from exc
