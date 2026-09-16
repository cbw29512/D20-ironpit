from __future__ import annotations

import logging

from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def savage_attacks_bonus_die(
    attacker: CombatantState,
    attack: WeaponAttack,
    critical: bool,
) -> tuple[int, str] | None:
    """Return the one extra weapon die granted by 2014 Half-Orc Savage Attacks."""
    try:
        if not critical:
            return None
        if CombatTrait.SAVAGE_ATTACKS not in attacker.template.combat_traits:
            return None
        if attack.weapon.attack_kind != WeaponAttackKind.MELEE:
            return None
        return attack.weapon.dice_size, attack.weapon.damage_type.value
    except Exception:
        logger.exception("Failed to evaluate Savage Attacks for %s.", attacker.template.name)
        raise
