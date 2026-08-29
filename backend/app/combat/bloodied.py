from __future__ import annotations

from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind
from app.domain.traits import CombatTrait


def bloodied_fury_advantage(state: CombatantState, attack: WeaponAttack) -> int:
    """Return one Advantage source for supported Bloodied Fury melee attacks."""
    if CombatTrait.BLOODIED_FURY not in state.template.combat_traits:
        return 0
    if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
        return 0
    return int(state.current_hp * 2 <= state.template.max_hp)
