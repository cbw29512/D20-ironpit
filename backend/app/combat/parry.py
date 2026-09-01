from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.modifier_stack import effective_armor_class
from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def resolve_parry_hit(
    defender: CombatantState,
    attack: WeaponAttack,
    attack_total: int,
    natural_roll: int,
    hit: bool,
) -> tuple[bool, bool]:
    """Use standard Parry only when its AC bonus converts a melee hit into a miss."""
    try:
        parry = defender.template.parry_reaction
        if not hit or parry is None or natural_roll == 20:
            return hit, False
        if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
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
