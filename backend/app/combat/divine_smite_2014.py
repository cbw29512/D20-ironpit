from __future__ import annotations

import logging

from app.combat.damage import BonusDamageSpec
from app.domain.models import CombatantState, DamageType, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def _available_slot_levels(state: CombatantState) -> list[int]:
    levels: list[int] = []
    for resource in state.resources:
        if not resource.id.startswith("spell-slot-") or resource.current_uses < 1:
            continue
        try:
            levels.append(int(resource.id.rsplit("-", 1)[1]))
        except ValueError:
            logger.exception("Invalid spell-slot resource id on %s: %s", state.template.name, resource.id)
            raise
    return levels


def divine_smite_bonus_damage(
    attacker: CombatantState,
    defender: CombatantState | None,
    attack: WeaponAttack,
) -> BonusDamageSpec | None:
    """Spend the highest available slot after a qualifying melee hit and return 2014 Smite dice."""
    try:
        if not attacker.template.progression_features.divine_smite_2014:
            return None
        if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
            return None
        available = _available_slot_levels(attacker)
        if not available:
            return None
        slot_level = max(available)
        resource = next(item for item in attacker.resources if item.id == f"spell-slot-{slot_level}")
        resource.current_uses -= 1
        dice_count = min(5, slot_level + 1)
        if defender is not None and (defender.template.creature_type or "").lower() in {"undead", "fiend"}:
            dice_count += 1
        return "Divine Smite", dice_count, 8, DamageType.RADIANT
    except Exception:
        logger.exception("Failed to resolve 2014 Divine Smite for %s", attacker.template.name)
        raise
