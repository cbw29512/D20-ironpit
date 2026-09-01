from __future__ import annotations

from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind
from app.domain.traits import CombatTrait


def is_bloodied(state: CombatantState) -> bool:
    """SRD 5.2.1 Bloodied: half Hit Points or fewer remaining."""
    return state.current_hp * 2 <= effective_max_hp(state)


def bloodied_fury_advantage(state: CombatantState, attack: WeaponAttack) -> int:
    """Return one Advantage source for supported Bloodied Fury melee attacks."""
    if CombatTrait.BLOODIED_FURY not in state.template.combat_traits:
        return 0
    if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
        return 0
    return int(is_bloodied(state))
