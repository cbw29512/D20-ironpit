from __future__ import annotations

from app.combat.bloodied import is_bloodied
from app.domain.models import CombatantState, ConditionalDamage, RollMode, WeaponAttack


def round1_initiative_lead(attacker: CombatantState, target: CombatantState, round_number: int | None) -> bool:
    return (
        round_number == 1
        and attacker.initiative_total is not None
        and target.initiative_total is not None
        and attacker.initiative_total > target.initiative_total
    )


def conditional_damage_active(
    conditional: ConditionalDamage,
    attacker: CombatantState,
    target: CombatantState | None,
    attack_mode: RollMode,
    round_number: int | None = None,
) -> bool:
    if conditional.trigger == "attack_advantage":
        return attack_mode is RollMode.ADVANTAGE
    if conditional.trigger == "attacker_bloodied":
        return is_bloodied(attacker)
    if target is None:
        raise ValueError("Target state is required for target-dependent conditional damage.")
    if conditional.trigger == "round1_initiative_lead":
        return round1_initiative_lead(attacker, target, round_number)
    if conditional.trigger == "target_bloodied":
        return is_bloodied(target)
    raise ValueError(f"Unsupported conditional damage trigger: {conditional.trigger!r}.")


def active_replacement_damage(
    attacker: CombatantState,
    target: CombatantState | None,
    attack: WeaponAttack,
    attack_mode: RollMode,
    round_number: int | None = None,
) -> ConditionalDamage | None:
    active = [
        item for item in attack.conditional_damage
        if item.mode == "replace_weapon"
        and conditional_damage_active(item, attacker, target, attack_mode, round_number)
    ]
    if len(active) > 1:
        raise ValueError(f"Multiple replacement damage profiles are active for {attack.id}.")
    return active[0] if active else None
