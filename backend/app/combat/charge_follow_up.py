from __future__ import annotations

import logging

from app.combat.charge_profiles import ChargeProfile
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)


def _attack_by_id(attacker: EncounterCombatant, attack_id: str) -> WeaponAttack | None:
    attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
    return next((attack for attack in attacks if attack.id == attack_id), None)


def _event_target(
    event: BattleEvent, fallback: EncounterCombatant, setup: EncounterSetup | None,
) -> EncounterCombatant:
    if setup is None:
        return fallback
    return next(
        (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == event.target_id),
        fallback,
    )


def resolve_charge_follow_up(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    profile: ChargeProfile,
    first_event: BattleEvent,
    dice: DiceProvider,
    setup: EncounterSetup | None,
) -> tuple[list[BattleEvent], int]:
    try:
        if not first_event.hit or profile.follow_up_attack_id is None:
            return [], sequence
        actual_target = _event_target(first_event, target, setup)
        if actual_target.state.current_hp <= 0 or actual_target.state.is_dead:
            return [], sequence
        attack = _attack_by_id(attacker, profile.follow_up_attack_id)
        if attack is None:
            raise ValueError(
                f"Charge follow-up attack {profile.follow_up_attack_id!r} is missing from {attacker.state.template.id}."
            )
        event = resolve_encounter_attack(
            sequence, round_number, attacker, actual_target, attack,
            combatant_distance(attacker, actual_target), dice, setup,
            spend_action=False, feature_id="charge-follow-up",
        )
        return [event], sequence + 1
    except Exception:
        logger.exception("Charge follow-up resolution failed for %s.", attacker.state.template.id)
        raise
