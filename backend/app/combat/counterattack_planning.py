from __future__ import annotations

import logging

from app.combat.attack_legality import attack_allowed_against
from app.combat.encounter_targeting import combatant_distance
from app.combat.range import resolve_attack_roll_mode
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)


def _member_by_id(setup: EncounterSetup, combatant_id: str) -> EncounterCombatant:
    try:
        matches = [
            member for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id == combatant_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one combatant {combatant_id!r}; found {len(matches)}."
            )
        return matches[0]
    except Exception as exc:
        logger.exception("Failed counterattack combatant lookup for %s.", combatant_id)
        raise RuntimeError("Counterattack combatant lookup failed.") from exc


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


def counterattack_plan(
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
            resolve_attack_roll_mode(counter.weapon, distance, close_enemy_active=True)
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
