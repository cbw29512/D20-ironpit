from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.attack_legality import attack_allowed_against
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.range import resolve_attack_roll_mode
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def _melee_attack_against_source(
    reactor: EncounterCombatant,
    source: EncounterCombatant,
) -> tuple[WeaponAttack, int] | None:
    """Choose the first declared legal melee weapon attack against the damage source."""
    try:
        distance = combatant_distance(reactor, source)
        attacks = [
            reactor.state.template.weapon_attack,
            *reactor.state.template.alternate_weapon_attacks,
        ]
        for attack in attacks:
            if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
                continue
            if not attack_allowed_against(attack, reactor.combatant_id, source.state):
                continue
            try:
                resolve_attack_roll_mode(
                    attack.weapon,
                    distance,
                    close_enemy_active=False,
                )
            except ValueError:
                continue
            return attack, distance
        return None
    except Exception as exc:
        logger.exception(
            "Failed to select damage-triggered melee reaction attack for %s.",
            reactor.combatant_id,
        )
        raise RuntimeError(
            "Damage-triggered melee reaction attack could not be selected."
        ) from exc


def resolve_damage_triggered_melee_reaction(
    sequence: int,
    round_number: int,
    reactor: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    *,
    turn_key: str | None = None,
) -> BattleEvent | None:
    """Spend one Reaction for a configured melee attack against the damage source."""
    try:
        rule = reactor.state.template.damage_triggered_melee_reaction
        if rule is None or not is_available(reactor.state, "reaction"):
            return None
        if source.combatant_id == reactor.combatant_id:
            return None
        if not source.state.is_alive or source.state.is_dead or source.state.current_hp <= 0:
            return None
        if combatant_distance(reactor, source) > rule.trigger_range_ft:
            return None

        selected = _melee_attack_against_source(reactor, source)
        if selected is None:
            return None
        attack, distance = selected
        spend(reactor.state, "reaction")
        return resolve_encounter_attack(
            sequence,
            round_number,
            reactor,
            source,
            attack,
            distance,
            dice,
            setup,
            spend_action=False,
            feature_id=rule.id,
            turn_key=turn_key,
            close_enemy_active=True,
            allow_reckless=False,
            off_turn=True,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Damage-triggered melee reaction failed for %s.",
            reactor.combatant_id,
        )
        raise RuntimeError(
            "Damage-triggered melee reaction could not be resolved."
        ) from exc
