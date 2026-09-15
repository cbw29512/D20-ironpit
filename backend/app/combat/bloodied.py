from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def is_bloodied(state: CombatantState) -> bool:
    """SRD 5.2.1 Bloodied: half Hit Points or fewer remaining."""
    try:
        return state.current_hp * 2 <= effective_max_hp(state)
    except Exception:
        logger.exception("Failed to evaluate Bloodied state for %s.", state.template.name)
        raise


def bloodied_attack_advantage(state: CombatantState, attack: WeaponAttack) -> int:
    """Return one Advantage source from a supported Bloodied attack trait."""
    try:
        if not is_bloodied(state):
            return 0
        if CombatTrait.BLOODIED_FRENZY in state.template.combat_traits:
            return 1
        if CombatTrait.BLOODIED_FURY in state.template.combat_traits and attack.weapon.attack_kind is WeaponAttackKind.MELEE:
            return 1
        return 0
    except Exception:
        logger.exception("Failed to evaluate Bloodied attack Advantage for %s.", state.template.name)
        raise


def bloodied_fury_advantage(state: CombatantState, attack: WeaponAttack) -> int:
    """Backward-compatible alias for the universal Bloodied attack Advantage resolver."""
    return bloodied_attack_advantage(state, attack)


def bloodied_saving_throw_advantage(state: CombatantState) -> int:
    """Return one Advantage source when a Bloodied trait grants Advantage on all saving throws."""
    try:
        return int(CombatTrait.BLOODIED_FRENZY in state.template.combat_traits and is_bloodied(state))
    except Exception:
        logger.exception("Failed to evaluate Bloodied saving-throw Advantage for %s.", state.template.name)
        raise
