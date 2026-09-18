from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.pit_policy import choose_attack
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _melee_zero_hp_triggered(events: list[BattleEvent], attacker: EncounterCombatant) -> bool:
    try:
        melee_ids = {
            attack.id
            for attack in [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
            if attack.weapon.attack_kind is WeaponAttackKind.MELEE
        }
        return any(
            event.event_type == "attack"
            and event.actor_id == attacker.combatant_id
            and event.weapon_id in melee_ids
            and (event.hp_before or 0) > 0
            and (event.hp_after or 0) <= 0
            for event in events
        )
    except Exception as exc:
        logger.exception("Failed Rampage trigger check for %s.", attacker.combatant_id)
        raise RuntimeError("Rampage trigger could not be evaluated.") from exc


def _bite_attack(attacker: EncounterCombatant) -> WeaponAttack:
    try:
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        bite = next(
            (
                attack for attack in attacks
                if attack.weapon.attack_kind is WeaponAttackKind.MELEE
                and attack.weapon.name.casefold() == "bite"
            ),
            None,
        )
        if bite is None:
            raise ValueError("Rampage requires a compiled Bite attack.")
        return bite
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed Rampage Bite lookup for %s.", attacker.combatant_id)
        raise RuntimeError("Rampage Bite attack could not be selected.") from exc


def resolve_rampage(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    prior_events: list[BattleEvent],
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve printed Rampage through shared movement, action economy, and attack rules."""
    try:
        if CombatTrait.RAMPAGE not in attacker.state.template.combat_traits:
            return [], sequence
        if not is_available(attacker.state, "bonus_action"):
            return [], sequence
        if not _melee_zero_hp_triggered(prior_events, attacker):
            return [], sequence

        bite = _bite_attack(attacker)
        choice = choose_attack(attacker, setup, [bite.id], kind=WeaponAttackKind.MELEE)
        events: list[BattleEvent] = []
        if choice is None:
            targets = living_opponents(attacker, setup)
            if not targets:
                return [], sequence
            target = min(targets, key=lambda item: combatant_distance(attacker, item))
            spend(attacker.state, "bonus_action")
            original_movement = attacker.state.movement_remaining_ft
            attacker.state.movement_remaining_ft = attacker.state.template.speed_ft // 2
            moved, sequence, _ = move_toward_with_reactions(
                sequence,
                round_number,
                attacker,
                target,
                setup,
                bite.weapon.reach_ft,
                dice,
                turn_key=turn_key,
            )
            events.extend(moved)
            attacker.state.movement_remaining_ft = original_movement
            if attacker.state.is_dead or attacker.state.is_unconscious:
                return events, sequence
            choice = choose_attack(attacker, setup, [bite.id], kind=WeaponAttackKind.MELEE)
            if choice is None:
                return events, sequence
        else:
            spend(attacker.state, "bonus_action")

        target, attack, distance = choice
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        events.append(resolve_attack(
            sequence,
            round_number,
            attacker.state,
            target.state,
            attack,
            distance,
            dice,
            actor_event_id=attacker.combatant_id,
            target_event_id=target.combatant_id,
            spend_action=False,
            feature_id="rampage",
            turn_key=turn_key,
            affected_states=affected,
        ))
        return events, sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Rampage resolution failed for %s.", attacker.combatant_id)
        raise RuntimeError("Rampage could not be resolved.") from exc
