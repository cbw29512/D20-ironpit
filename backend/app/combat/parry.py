from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import has_condition
from app.combat.modifier_stack import effective_armor_class
from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def _wielded_attack(state: CombatantState) -> WeaponAttack | None:
    attack_id = state.wielded_attack_id or state.template.weapon_attack.id
    return next(
        (attack for attack in [state.template.weapon_attack, *state.template.alternate_weapon_attacks]
         if attack.id == attack_id),
        None,
    )


def _can_see_attacker(defender: CombatantState, attacker: CombatantState) -> bool:
    # The Iron Pit has clear line of sight by default. Supported visibility effects still apply.
    if has_condition(defender, "blinded"):
        return False
    if has_condition(attacker, "invisible"):
        # Fail closed until blindsight/truesight ranges are represented in the universal template.
        return False
    return True


def resolve_parry_hit(
    defender: CombatantState,
    attacker: CombatantState,
    attack: WeaponAttack,
    attack_total: int,
    natural_roll: int,
    hit: bool,
) -> tuple[bool, bool]:
    """Resolve SRD Parry only when every printed trigger requirement is satisfied."""
    try:
        parry = defender.template.parry_reaction
        if not hit or parry is None or natural_roll == 20:
            return hit, False
        if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
            return hit, False
        if not _can_see_attacker(defender, attacker):
            return hit, False
        wielded = _wielded_attack(defender)
        if wielded is None or wielded.weapon.attack_kind is not WeaponAttackKind.MELEE:
            return hit, False
        if not is_available(defender, "reaction"):
            return hit, False
        if attack_total >= effective_armor_class(defender) + parry.ac_bonus:
            return hit, False
        spend(defender, "reaction")
        return False, True
    except Exception as exc:
        logger.exception("Parry resolution failed for %s.", defender.template.id)
        raise RuntimeError("Parry reaction could not be resolved.") from exc
