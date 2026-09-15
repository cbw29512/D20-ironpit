from __future__ import annotations

from app.combat.ability_scores import ability_modifier_delta
from app.domain.models import CombatantState, WeaponAttack


def effective_attack_bonus(attacker: CombatantState, attack: WeaponAttack) -> int:
    if attack.attack_ability is None:
        return attack.attack_bonus
    return attack.attack_bonus + ability_modifier_delta(attacker, attack.attack_ability)
