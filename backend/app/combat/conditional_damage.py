from __future__ import annotations

from app.combat.bloodied import is_bloodied
from app.domain.models import CombatantState, ConditionalDamage, RollMode, WeaponAttack


def conditional_damage_active(
    conditional: ConditionalDamage,
    attacker: CombatantState,
    target: CombatantState | None,
    attack_mode: RollMode,
) -> bool:
    if conditional.trigger == "attack_advantage":
        return attack_mode is RollMode.ADVANTAGE
    if conditional.trigger == "attacker_bloodied":
        return is_bloodied(attacker)
    if conditional.trigger == "round1_initiative_lead":
        if target is None:
            raise ValueError("Opening-initiative damage requires defender state.")
        return (attacker.turns_started == 1 and target.turns_started == 0
                and attacker.feature_use_counts.get("weapon_attack_attempts", 0) == 1)
    if target is None:
        raise ValueError("Target state is required for target-Bloodied conditional damage.")
    return is_bloodied(target)


def active_replacement_damage(
    attacker: CombatantState,
    target: CombatantState | None,
    attack: WeaponAttack,
    attack_mode: RollMode,
) -> ConditionalDamage | None:
    active = [
        item for item in attack.conditional_damage
        if item.mode == "replace_weapon" and conditional_damage_active(item, attacker, target, attack_mode)
    ]
    if len(active) > 1:
        raise ValueError(f"Multiple replacement damage profiles are active for {attack.id}.")
    return active[0] if active else None
