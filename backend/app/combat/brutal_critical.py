from __future__ import annotations

import logging

from app.domain.models import CombatantState, DamageType, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)
BrutalCriticalSpec = tuple[str, int, int, DamageType]


def brutal_critical_bonus(
    attacker: CombatantState,
    attack: WeaponAttack,
    critical: bool,
) -> BrutalCriticalSpec | None:
    """Return the 2014 Barbarian's extra weapon damage dice on a melee critical hit."""
    try:
        extra = attacker.template.progression_features.brutal_critical_extra_dice
        if not critical or extra <= 0 or attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
            return None
        return ("Brutal Critical", extra, attack.weapon.dice_size, attack.weapon.damage_type)
    except Exception as exc:
        logger.exception("Brutal Critical resolution failed for %s.", attacker.template.name)
        raise RuntimeError("Brutal Critical could not be resolved.") from exc
