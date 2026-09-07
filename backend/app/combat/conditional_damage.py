from __future__ import annotations

from app.combat.bloodied import is_bloodied
from app.domain.models import CombatantState, ConditionalDamage, RollMode, WeaponAttack


def conditional_damage_active(
    conditional: ConditionalDamage,
    attacker: CombatantState,
    target: CombatantState | None,
    attack_mode: RollMode,
    attacker_id: str | None = None,
) -> bool:
    if conditional.trigger == "attack_advantage":
        return attack_mode is RollMode.ADVANTAGE
    if conditional.trigger == "attacker_bloodied":
        return is_bloodied(attacker)
    if target is None:
        raise ValueError("Target state is required for target-dependent conditional damage.")
    if conditional.trigger == "target_grappled_by_self":
        return attacker_id is not None and any(source.source_id == attacker_id for source in target.grapple_sources)
    return is_bloodied(target)


def active_replacement_damage(
    attacker: CombatantState,
    target: CombatantState | None,
    attack: WeaponAttack,
    attack_mode: RollMode,
    attacker_id: str | None = None,
) -> ConditionalDamage | None:
    active = [
        item for item in attack.conditional_damage
        if item.mode == "replace_weapon" and conditional_damage_active(
            item, attacker, target, attack_mode, attacker_id,
        )
    ]
    if len(active) > 1:
        raise ValueError(f"Multiple replacement damage profiles are active for {attack.id}.")
    return active[0] if active else None
