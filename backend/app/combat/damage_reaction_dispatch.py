from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.action_economy import is_available
from app.combat.damage_reaction_eligibility import DamageReactionTrigger, damage_reaction_is_eligible
from app.combat.pit_policy import choose_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DamageReactionPlan:
    """Proven runtime plan for one immediate damage-triggered reaction attack."""

    reactor: EncounterCombatant
    source: EncounterCombatant
    attack: WeaponAttack
    distance_ft: int


def plan_damage_reaction_attack(
    reactor: EncounterCombatant,
    source: EncounterCombatant,
    setup: EncounterSetup,
    applied_damage: int,
    *,
    reactor_can_react: bool = True,
) -> DamageReactionPlan | None:
    """Fail closed unless the trigger and a legal melee counterattack are both proven."""
    try:
        policy = reactor.state.template.damage_reaction_attack
        if policy is None:
            return None
        chosen = choose_attack(
            reactor,
            setup,
            [
                reactor.state.template.weapon_attack.id,
                *(attack.id for attack in reactor.state.template.alternate_weapon_attacks),
            ],
            kind=WeaponAttackKind.MELEE,
        )
        if chosen is None:
            return None
        target, attack, distance_ft = chosen
        if target.combatant_id != source.combatant_id:
            return None
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
    except Exception:
        logger.exception("Damage reaction planning failed closed for %s.", reactor.combatant_id)
        return None
