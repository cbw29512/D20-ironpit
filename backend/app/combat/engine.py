from __future__ import annotations

import logging
import uuid

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.attacks import resolve_attack
from app.combat.action_economy import is_available
from app.combat.dice import DiceProvider
from app.combat.exhaustion import ability_check_disadvantage_sources, d20_modifier
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.rolls import roll_d20
from app.combat.start_turn import begin_turn_with_events
from app.combat.state import build_combatant_state
from app.combat.turns import prepare_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
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
        fighter_member = EncounterCombatant(
            combatant_id=fighter.template.id, side="heroes", position_ft=0, state=fighter,
        )
        monster_member = EncounterCombatant(
            combatant_id=monster.template.id, side="monsters", position_ft=starting_distance_ft, state=monster,
        )
        duel_setup = EncounterSetup(
            heroes=[fighter_member],
            monsters=[monster_member],
            hero_total_levels=max(1, fighter.template.level or 1),
            monster_total_cr="legacy-duel",
        )

        for state in (fighter, monster):
            initiative_mode = ability_check_roll_mode(
                state,
                advantage_sources=int(state.template.progression_features.initiative_advantage),
                disadvantage_sources=ability_check_disadvantage_sources(state),
            )
            initiative = roll_d20(
                dice, state.template.initiative_bonus + d20_modifier(state), initiative_mode,
            )
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
            for state in order:
                state.current_round = round_number
            for attacker in order:
                defender = monster if attacker is fighter else fighter
                if attacker.current_hp <= 0 or defender.current_hp <= 0:
                    continue

                start_events, sequence = begin_turn_with_events(
                    sequence, round_number, attacker.template.id, attacker, dice,
                )
                events.extend(start_events)
                member = fighter_member if attacker is fighter else monster_member
                turn_key = f"{round_number}:{member.combatant_id}"
                healing_choice = choose_healing_action(member, duel_setup, turn_key)
                if healing_choice is not None:
                    healing_action, healing_target = healing_choice
                    events.append(resolve_healing(
                        sequence, round_number, member, healing_target, healing_action, dice, turn_key,
                    ))
                    sequence += 1
                if not is_available(attacker, "action"):
                    continue

                weapon, prep_events, sequence = prepare_attack(
                    sequence,
                    round_number,
                    attacker,
                    battlefield,
                )
                events.extend(prep_events)
                if weapon is None:
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

                if defender.current_hp <= 0:
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
