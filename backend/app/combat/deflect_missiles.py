from __future__ import annotations

import logging

from app.combat.attack_damage_reduction import (
    apply_attack_damage_reduction,
    can_reduce_attack_damage,
)
from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageRollComponent, WeaponAttack

logger = logging.getLogger(__name__)


def can_deflect_missiles(defender: CombatantState, attack: WeaponAttack) -> bool:
    """Compatibility wrapper for certified 2014 Deflect Missiles."""
    try:
        return can_reduce_attack_damage(defender, attack, [
            DamageRollComponent(
                source=attack.weapon.name,
                notation="1",
                rolls=[],
                modifier=0,
                damage_type=attack.weapon.damage_type,
                total=1,
            ),
        ])
    except Exception:
        logger.exception("Failed Deflect Missiles eligibility check for %s", defender.template.id)
        raise


def apply_deflect_missiles(
    defender: CombatantState,
    attack: WeaponAttack,
    components: list[DamageRollComponent],
    dice: DiceProvider,
) -> tuple[list[DamageRollComponent], bool, int]:
    """Compatibility wrapper over the universal attack-damage reduction Reaction."""
    try:
        result = apply_attack_damage_reduction(defender, attack, components, dice)
        used = result.used and result.source_id == "deflect-missiles"
        return result.components, used, result.reduction if used else 0
    except Exception:
        logger.exception("Failed Deflect Missiles resolution for %s", defender.template.id)
        raise
