from __future__ import annotations

from dataclasses import dataclass

from app.combat.damage import BonusDamageSpec, aggregate_damage_components, resolve_weapon_damage
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.on_hit_save_damage import OnHitSaveDamageResolution, resolve_on_hit_save_damage
from app.combat.zero_hp import apply_damage
from app.domain.models import CombatantState, DamageRollComponent, DiceRoll, RollMode, WeaponAttack


@dataclass(frozen=True)
class AttackHitDamageResolution:
    damage_roll: DiceRoll
    damage_components: list[DamageRollComponent]
    damage_outcome: str | None
    applied_total: int
    save_damage: OnHitSaveDamageResolution


def resolve_attack_hit_damage(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    critical: bool,
    attack_mode: RollMode,
    turn_key: str,
    bonus_damage: BonusDamageSpec | None,
    affected_states: list[CombatantState] | None,
    sneak_attack_ally_available: bool,
) -> AttackHitDamageResolution:
    damage_roll, rolled_components = resolve_weapon_damage(
        attacker, attack, dice, critical, attack_mode, turn_key, bonus_damage=bonus_damage,
        target=defender, sneak_attack_ally_available=sneak_attack_ally_available,
    )
    save_damage = resolve_on_hit_save_damage(defender, attack, dice)
    if save_damage.component is not None:
        rolled_components.append(save_damage.component)
        damage_roll = aggregate_damage_components(rolled_components)
    applied_total, components = apply_damage_defenses(defender, rolled_components)
    damage_roll.total = applied_total
    applied_types = {part.damage_type for part in components if part.applied_total > 0}
    outcome = apply_damage(
        defender, applied_total, critical=critical, damage_types=applied_types,
        dice=dice, affected_states=affected_states,
    )
    return AttackHitDamageResolution(damage_roll, components, outcome, applied_total, save_damage)
