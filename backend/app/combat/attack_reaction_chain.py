from __future__ import annotations

import logging

from app.combat.attack_legality import attack_allowed_against
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.range import resolve_attack_roll_mode
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)
_MAX_REACTION_DEPTH = 8


def _member_by_id(setup: EncounterSetup, combatant_id: str) -> EncounterCombatant:
    try:
        matches = [
            member
            for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id == combatant_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one combatant {combatant_id!r}; found {len(matches)}."
            )
        return matches[0]
    except Exception as exc:
        logger.exception("Failed reaction-chain combatant lookup for %s.", combatant_id)
        raise RuntimeError("Reaction-chain combatant lookup failed.") from exc


def _attack_by_id(member: EncounterCombatant, attack_id: str) -> WeaponAttack:
    try:
        attacks = [
            member.state.template.weapon_attack,
            *member.state.template.alternate_weapon_attacks,
        ]
        matches = [attack for attack in attacks if attack.id == attack_id]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one counterattack {attack_id!r}; found {len(matches)}."
            )
        return matches[0]
    except Exception as exc:
        logger.exception(
            "Failed counterattack lookup for %s attack=%s.",
            member.combatant_id,
            attack_id,
        )
        raise RuntimeError("Counterattack binding could not be resolved.") from exc


def _counterattack(
    event: BattleEvent,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[EncounterCombatant, WeaponAttack, int] | None:
    try:
        if event.defensive_reaction_id is None:
            return None
        if event.target_id is None or event.hit is not False:
            raise ValueError("Defensive reaction evidence requires a missed attack target.")
        reactor = _member_by_id(setup, event.target_id)
        rule = reactor.state.template.parry_reaction
        if rule is None or rule.source_feature != event.defensive_reaction_id:
            raise ValueError("Defensive reaction evidence does not match runtime state.")
        if rule.counterattack_attack_id is None:
            return None
        if not reactor.state.is_alive or reactor.state.is_dead:
            return None
        if not attacker.state.is_alive or attacker.state.is_dead:
            return None

        counter = _attack_by_id(reactor, rule.counterattack_attack_id)
        distance = combatant_distance(reactor, attacker)
        if distance > rule.counterattack_range_ft:
            return None
        if not attack_allowed_against(counter, reactor.combatant_id, attacker.state):
            return None
        try:
            resolve_attack_roll_mode(
                counter.weapon,
                distance,
                close_enemy_active=True,
            )
        except ValueError:
            return None
        return reactor, counter, distance
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to plan counterattack after reaction %s.",
            event.defensive_reaction_id,
        )
        raise RuntimeError("Counterattack planning failed.") from exc


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
        event = resolve_encounter_attack(
            sequence,
            round_number,
            attacker,
            target,
            attack,
            distance_ft,
            dice,
            setup,
            **attack_options,
        )
        events = [event]
        sequence += 1

        planned = _counterattack(event, attacker, setup)
        if planned is None:
            return events, sequence
        reactor, counter, counter_distance = planned
        rule = reactor.state.template.parry_reaction
        if rule is None:
            raise RuntimeError("Counterattack reaction state disappeared.")

        more, sequence = resolve_attack_event_chain(
            sequence,
            round_number,
            reactor,
            attacker,
            counter,
            counter_distance,
            dice,
            setup,
            reaction_depth=reaction_depth + 1,
            spend_action=False,
            feature_id=rule.source_feature,
            turn_key=attack_options.get("turn_key"),
            close_enemy_active=True,
            allow_reckless=False,
            off_turn=True,
        )
        events.extend(more)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Attack reaction chain failed: attacker=%s target=%s attack=%s.",
            attacker.combatant_id,
            target.combatant_id,
            attack.id,
        )
        raise RuntimeError("Attack reaction chain could not be resolved.") from exc
