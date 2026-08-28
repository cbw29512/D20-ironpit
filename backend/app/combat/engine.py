from __future__ import annotations

import logging
import uuid

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.fighter import use_second_wind
from app.combat.policy import should_use_second_wind
from app.combat.rolls import roll_d20
from app.combat.state import (
    begin_turn,
    build_combatant_state,
    end_turn,
    expire_attack_roll_effects_at_turn_start,
)
from app.combat.turns import prepare_attack, prepare_skirmish_retreat
from app.domain.models import BattleEvent, BattlefieldState, BattleResult, CombatantTemplate

logger = logging.getLogger(__name__)
MAX_ROUNDS = 100


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
        events: list[BattleEvent] = []
        sequence = 1

        for state in (fighter, monster):
            initiative = roll_d20(dice, state.template.initiative_bonus)
            state.initiative_roll = initiative.selected_roll
            state.initiative_total = initiative.total
            events.append(BattleEvent(
                sequence=sequence,
                round_number=0,
                event_type="initiative",
                actor_id=state.template.id,
                actor_name=state.template.name,
                attack_roll=initiative,
                animation="initiative",
                description=f"{state.template.name} rolls initiative {state.initiative_total}.",
            ))
            sequence += 1

        order = sorted(
            (fighter, monster),
            key=lambda state: (state.initiative_total or 0, state.template.initiative_bonus),
            reverse=True,
        )

        for round_number in range(1, MAX_ROUNDS + 1):
            for attacker in order:
                defender = monster if attacker is fighter else fighter
                if not attacker.is_alive or not defender.is_alive:
                    continue

                expire_attack_roll_effects_at_turn_start(attacker, (fighter, monster))
                begin_turn(attacker)
                if attacker is fighter and should_use_second_wind(fighter):
                    events.append(use_second_wind(sequence, round_number, fighter, dice))
                    sequence += 1

                retreat_events, sequence = prepare_skirmish_retreat(
                    sequence, round_number, attacker, battlefield
                )
                events.extend(retreat_events)
                weapon, prep_events, sequence = prepare_attack(
                    sequence,
                    round_number,
                    attacker,
                    battlefield,
                )
                events.extend(prep_events)
                if weapon is None:
                    end_turn(attacker)
                    continue

                event = resolve_attack(
                    sequence,
                    round_number,
                    attacker,
                    defender,
                    weapon,
                    battlefield.distance_ft,
                    dice,
                )
                events.append(event)
                sequence += 1
                end_turn(attacker)

                if not defender.is_alive:
                    events.append(BattleEvent(
                        sequence=sequence,
                        round_number=round_number,
                        event_type="victory",
                        actor_id=attacker.template.id,
                        actor_name=attacker.template.name,
                        target_id=defender.template.id,
                        target_name=defender.template.name,
                        animation="victory",
                        description=f"{attacker.template.name} wins the duel.",
                    ))
                    return BattleResult(
                        battle_id=str(uuid.uuid4()),
                        winner_id=attacker.template.id,
                        winner_name=attacker.template.name,
                        rounds=round_number,
                        fighter=fighter,
                        monster=monster,
                        battlefield=battlefield,
                        events=events,
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
        return BattleResult(
            battle_id=str(uuid.uuid4()),
            winner_id=None,
            winner_name=None,
            rounds=MAX_ROUNDS,
            fighter=fighter,
            monster=monster,
            battlefield=battlefield,
            events=events,
        )
    except Exception as exc:
        logger.exception("Duel execution failed.")
        raise RuntimeError("Duel execution failed.") from exc
