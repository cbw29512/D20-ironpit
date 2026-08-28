from __future__ import annotations

import logging
import uuid

from app.combat.attack_actions import resolve_attack_action
from app.combat.battle_start import resolve_battle_start
from app.combat.conditions import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.fighter import use_second_wind
from app.combat.policy import should_use_second_wind
from app.combat.state import (
    begin_turn,
    build_combatant_state,
    end_turn,
    expire_attack_roll_effects_at_turn_start,
)
from app.combat.turns import prepare_attack, prepare_nimble_hide, prepare_skirmish_retreat
from app.domain.models import (
    ActorVisibilityState,
    BattleEvent,
    BattlefieldState,
    BattleResult,
    CombatantTemplate,
    EncounterSetup,
)

logger = logging.getLogger(__name__)
MAX_ROUNDS = 100


def run_duel(
    fighter_template: CombatantTemplate,
    monster_template: CombatantTemplate,
    dice: DiceProvider,
    starting_distance_ft: int = 5,
    visibility_by_actor: dict[str, ActorVisibilityState] | None = None,
    encounter_setup: EncounterSetup | None = None,
) -> BattleResult:
    try:
        fighter = build_combatant_state(fighter_template)
        monster = build_combatant_state(monster_template)
        combatants = (fighter, monster)
        battlefield = BattlefieldState(
            starting_distance_ft=starting_distance_ft,
            distance_ft=starting_distance_ft,
            visibility_by_actor=visibility_by_actor or {},
        )
        events, order, sequence = resolve_battle_start(
            combatants, battlefield, dice, encounter_setup
        )

        for round_number in range(1, MAX_ROUNDS + 1):
            for attacker in order:
                defender = monster if attacker is fighter else fighter
                if not attacker.is_alive or not defender.is_alive:
                    continue

                expire_attack_roll_effects_at_turn_start(attacker, combatants)
                begin_turn(attacker, combatants)
                if is_incapacitated(attacker):
                    end_turn(attacker, combatants)
                    continue
                if attacker is fighter and should_use_second_wind(fighter):
                    events.append(use_second_wind(sequence, round_number, fighter, dice))
                    sequence += 1

                retreat_events, sequence = prepare_skirmish_retreat(
                    sequence,
                    round_number,
                    attacker,
                    defender,
                    battlefield,
                    dice,
                )
                events.extend(retreat_events)
                hide_events, sequence = prepare_nimble_hide(
                    sequence, round_number, attacker, battlefield, dice
                )
                events.extend(hide_events)
                weapon, prep_events, sequence = prepare_attack(
                    sequence, round_number, attacker, battlefield
                )
                events.extend(prep_events)
                if weapon is None:
                    end_turn(attacker, combatants)
                    continue

                attack_events, sequence = resolve_attack_action(
                    sequence,
                    round_number,
                    attacker,
                    defender,
                    weapon,
                    battlefield.distance_ft,
                    dice,
                    battlefield=battlefield,
                )
                events.extend(attack_events)
                end_turn(attacker, combatants)

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
