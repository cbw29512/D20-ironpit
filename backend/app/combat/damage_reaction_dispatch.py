from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.action_economy import is_available, spend
from app.combat.attack_legality import attack_allowed_against
from app.combat.condition_rules import is_incapacitated
from app.combat.damage_reaction_eligibility import DamageReactionTrigger, damage_reaction_is_eligible
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.range import resolve_attack_roll_mode
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DamageReactionPlan:
    """Proven runtime plan for one immediate damage-triggered reaction attack."""

    reactor: EncounterCombatant
    source: EncounterCombatant
    attack: WeaponAttack
    distance_ft: int


def _legal_melee_attack_against_source(
    reactor: EncounterCombatant,
    source: EncounterCombatant,
) -> tuple[WeaponAttack, int] | None:
    """Choose the first declared melee attack that is legal against the triggering source."""
    try:
        distance_ft = combatant_distance(reactor, source)
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
                resolve_attack_roll_mode(attack.weapon, distance_ft, close_enemy_active=False)
            except ValueError:
                continue
            return attack, distance_ft
        return None
    except Exception as exc:
        logger.exception(
            "Failed to select source-bound damage reaction attack: reactor=%s source=%s.",
            reactor.combatant_id,
            source.combatant_id,
        )
        raise RuntimeError("Damage reaction attack selection failed.") from exc


def plan_damage_reaction_attack(
    reactor: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    applied_damage: int,
) -> DamageReactionPlan | None:
    """Fail closed unless the source-bound trigger and melee counterattack are both legal."""
    del setup  # Reserved for future arena-wide reaction policy without changing this contract.
    try:
        policy = reactor.state.template.damage_reaction_attack
        if policy is None or source.combatant_id == reactor.combatant_id:
            return None
        if not source.state.is_alive or source.state.is_dead or source.state.current_hp <= 0:
            return None

        selected = _legal_melee_attack_against_source(reactor, source)
        if selected is None:
            return None
        attack, distance_ft = selected
        reactor_can_react = bool(
            reactor.state.is_alive
            and not reactor.state.is_dead
            and reactor.state.current_hp > 0
            and not is_incapacitated(reactor.state)
        )
        trigger = DamageReactionTrigger(
            applied_damage=applied_damage,
            source_is_creature=True,
            source_distance_ft=distance_ft,
            reaction_available=is_available(reactor.state, "reaction"),
            reactor_can_react=reactor_can_react,
        )
        if not damage_reaction_is_eligible(policy, trigger):
            return None
        return DamageReactionPlan(reactor=reactor, source=source, attack=attack, distance_ft=distance_ft)
    except Exception as exc:
        logger.exception(
            "Damage reaction planning failed: reactor=%s source=%s.",
            reactor.combatant_id,
            source.combatant_id,
        )
        raise RuntimeError("Damage reaction planning failed.") from exc


def resolve_damage_reaction_attack(
    sequence: int,
    round_number: int,
    reactor: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    applied_damage: int,
    dice: DiceProvider,
    *,
    turn_key: str | None = None,
) -> BattleEvent | None:
    """Spend the Reaction and immediately resolve the planned off-turn melee attack."""
    try:
        plan = plan_damage_reaction_attack(reactor, source, setup, applied_damage)
        if plan is None:
            return None
        policy = reactor.state.template.damage_reaction_attack
        if policy is None:
            raise RuntimeError("Damage reaction policy disappeared after planning.")

        spend(reactor.state, "reaction")
        return resolve_encounter_attack(
            sequence,
            round_number,
            reactor,
            source,
            plan.attack,
            plan.distance_ft,
            dice,
            setup,
            spend_action=False,
            feature_id=policy.source_feature,
            turn_key=turn_key,
            close_enemy_active=True,
            allow_reckless=False,
            off_turn=True,
        )
    except Exception as exc:
        logger.exception(
            "Damage reaction resolution failed: reactor=%s source=%s sequence=%s.",
            reactor.combatant_id,
            source.combatant_id,
            sequence,
        )
        raise RuntimeError("Damage reaction attack resolution failed.") from exc
