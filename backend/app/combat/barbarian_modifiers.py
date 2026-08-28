from __future__ import annotations

import logging

from app.combat.conditions import is_incapacitated
from app.domain.models import AbilityKind, CombatantState, DamageRollComponent, WeaponAttack

logger = logging.getLogger(__name__)


def is_raging(state: CombatantState) -> bool:
    return bool(state.raging and not is_incapacitated(state))


def rage_damage_bonus(level: int | None) -> int:
    if level is None or level < 1:
        return 0
    if level >= 16:
        return 4
    if level >= 9:
        return 3
    return 2


def rage_strength_save_advantage(actor: CombatantState, ability: AbilityKind) -> int:
    return int(is_raging(actor) and ability is AbilityKind.STRENGTH)


def rage_damage_component(
    actor: CombatantState,
    attack: WeaponAttack,
) -> DamageRollComponent | None:
    try:
        if not is_raging(actor) or attack.ability is not AbilityKind.STRENGTH:
            return None
        bonus = rage_damage_bonus(actor.template.level)
        if bonus <= 0:
            return None
        return DamageRollComponent(
            source="Rage",
            notation=f"{bonus:+d}",
            rolls=[],
            modifier=bonus,
            damage_type=attack.weapon.damage_type,
            total=bonus,
        )
    except Exception as exc:
        logger.exception("Rage damage failed for %s.", actor.template.name)
        raise RuntimeError("Rage damage could not be resolved.") from exc
