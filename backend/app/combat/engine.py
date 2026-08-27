from __future__ import annotations

import logging
import uuid

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import DiceProvider
from app.combat.fighter import use_second_wind
from app.combat.policy import should_use_second_wind
from app.combat.range import resolve_attack_roll_mode
from app.combat.rolls import roll_d20
from app.combat.state import begin_turn, build_combatant_state
from app.combat.turns import prepare_attack
from app.domain.models import (
    BattleEvent,
    BattlefieldState,
    BattleResult,
    CombatantState,
    CombatantTemplate,
    Weapon,
)

logger = logging.getLogger(__name__)
MAX_ROUNDS = 100


def _resolve_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    weapon: Weapon,
    distance_ft: int,
    dice: DiceProvider,
) -> BattleEvent:
    try:
        if not attacker.action_available:
            raise ValueError("Action is not available for an attack.")
        mode = resolve_attack_roll_mode(weapon, distance_ft)
        attack_roll = roll_d20(dice, weapon.attack_bonus, mode)
        attacker.action_available = False
        natural = attack_roll.selected_roll or 0
        critical = natural == 20
        hit = natural != 1 and (critical or attack_roll.total >= defender.template.armor_class)
        hp_before = defender.current_hp
        damage_roll = None
        damage_components = []
        if hit:
            damage_roll, damage_components = resolve_weapon_damage(
                attacker, weapon, dice, critical, mode
            )
            defender.current_hp = max(0, defender.current_hp - damage_roll.total)
            defender.is_alive = defender.current_hp > 0

        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack",
            actor_id=attacker.template.id, actor_name=attacker.template.name,
            target_id=defender.template.id, target_name=defender.template.name,
            attack_roll=attack_roll, damage_roll=damage_roll,
            damage_components=damage_components, hit=hit, critical=critical,
            hp_before=hp_before, hp_after=defender.current_hp,
            weapon_id=weapon.id, projectile=weapon.projectile,
            animation=weapon.animation,
            description=f"{attacker.template.name}: {outcome} with {weapon.name}.",
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc


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
                sequence=sequence, round_number=0, event_type="initiative",
                actor_id=state.template.id, actor_name=state.template.name,
                attack_roll=initiative, animation="initiative",
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
                begin_turn(attacker)
                if attacker is fighter and should_use_second_wind(fighter):
                    events.append(use_second_wind(sequence, round_number, fighter, dice))
                    sequence += 1

                weapon, prep_events, sequence = prepare_attack(
                    sequence, round_number, attacker, battlefield
                )
                events.extend(prep_events)
                if weapon is None:
                    continue

                event = _resolve_attack(
                    sequence, round_number, attacker, defender,
                    weapon, battlefield.distance_ft, dice,
                )
                events.append(event)
                sequence += 1
                if not defender.is_alive:
                    events.append(BattleEvent(
                        sequence=sequence, round_number=round_number, event_type="victory",
                        actor_id=attacker.template.id, actor_name=attacker.template.name,
                        target_id=defender.template.id, target_name=defender.template.name,
                        animation="victory", description=f"{attacker.template.name} wins the duel.",
                    ))
                    return BattleResult(
                        battle_id=str(uuid.uuid4()), winner_id=attacker.template.id,
                        winner_name=attacker.template.name, rounds=round_number,
                        fighter=fighter, monster=monster, battlefield=battlefield, events=events,
                    )

        events.append(BattleEvent(
            sequence=sequence, round_number=MAX_ROUNDS, event_type="draw",
            actor_id="arena", actor_name="Arena", animation="draw",
            description=f"The duel reached the {MAX_ROUNDS}-round safety limit.",
        ))
        return BattleResult(
            battle_id=str(uuid.uuid4()), winner_id=None, winner_name=None,
            rounds=MAX_ROUNDS, fighter=fighter, monster=monster,
            battlefield=battlefield, events=events,
        )
    except Exception as exc:
        logger.exception("Duel execution failed.")
        raise RuntimeError("Duel execution failed.") from exc
