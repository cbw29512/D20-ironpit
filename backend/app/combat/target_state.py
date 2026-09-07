from __future__ import annotations

from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState
from app.domain.traits import CombatTrait


def target_missing_hp_attack_advantage(attacker: CombatantState, defender: CombatantState) -> int:
    """Return one Advantage source when the attacker keys off an injured target."""
    return int(
        CombatTrait.TARGET_MISSING_HP_ATTACK_ADVANTAGE in attacker.template.combat_traits
        and defender.current_hp < effective_max_hp(defender)
    )
