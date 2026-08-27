from __future__ import annotations

import logging
import uuid

from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.models import BattleEvent, BattleResult, CombatantState, CombatantTemplate, DiceRoll, RollMode

logger = logging.getLogger(__name__)
MAX_ROUNDS = 100


def _roll_damage(attacker: CombatantState, dice: DiceProvider, critical: bool) -> DiceRoll:
    try:
        weapon = attacker.template.weapon
        count = weapon.dice_count * (2 if critical else 1)
        rolls = [dice.roll(weapon.dice_size) for _ in range(count)]
        total = sum(rolls) + weapon.damage_bonus
        return DiceRoll(
            notation=f"{count}d{weapon.dice_size}+{weapon.damage_bonus}",
            rolls=rolls,
            modifier=weapon.damage_bonus,
            total=total,
        )
    except Exception as exc:
        logger.exception("Damage resolution failed for %s.", attacker.template.name)
        raise RuntimeError("Damage resolution failed.") from exc


def _resolve_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    dice: DiceProvider,
    mode: RollMode = RollMode.NORMAL,
) -> BattleEvent:
    try:
        attack_roll = roll_d20(dice, attacker.template.weapon.attack_bonus, mode)
        natural = attack_roll.selected_roll or 0
        critical = natural == 20
        hit = natural != 1 and (critical or attack_roll.total >= defender.template.armor_class)
        hp_before = defender.current_hp
        damage = _roll_damage(attacker, dice, critical) if hit else None
        if damage:
            defender.current_hp = max(0, defender.current_hp - damage.total)
            defender.is_alive = defender.current_hp > 0
        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="attack",
            actor_id=attacker.template.id,
            actor_name=attacker.template.name,
            target_id=defender.template.id,
            target_name=defender.template.name,
            attack_roll=attack_roll,
            damage_roll=damage,
            hit=hit,
            critical=critical,
            hp_before=hp_before,
            hp_after=defender.current_hp,
            animation=attacker.template.weapon.animation,
            description=f"{attacker.template.name}: {outcome} with {attacker.template.weapon.name}.",
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc


def run_duel(
    fighter_template: CombatantTemplate,
    monster_template: CombatantTemplate,
    dice: DiceProvider,
) -> BattleResult:
    try:
        fighter = CombatantState(template=fighter_template, current_hp=fighter_template.max_hp)
        monster = CombatantState(template=monster_template, current_hp=monster_template.max_hp)
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
                event = _resolve_attack(sequence, round_number, attacker, defender, dice)
                events.append(event)
                sequence += 1
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
            events=events,
        )
    except Exception as exc:
        logger.exception("Duel execution failed.")
        raise RuntimeError("Duel execution failed.") from exc
