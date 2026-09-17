from __future__ import annotations

from dataclasses import dataclass

from app.combat.damage import BonusDamageSpec, aggregate_damage_components, resolve_weapon_damage
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.deflect_missiles import apply_deflect_missiles
from app.combat.dice import DiceProvider
from app.combat.on_hit_save_damage import OnHitSaveDamageResolution, resolve_on_hit_save_damage
from app.combat.rogue_defenses import apply_uncanny_dodge
from app.combat.zero_hp import apply_damage
from app.combat.zero_hp_save_damage_rider import apply_zero_hp_save_damage_rider, save_damage_caused_zero
from app.domain.models import CombatantState, DamageRollComponent, DiceRoll, RollMode, WeaponAttack


@dataclass(frozen=True)
class AttackHitDamageResolution:
    damage_roll: DiceRoll
    damage_components: list[DamageRollComponent]
    damage_outcome: str | None
    applied_total: int
    save_damage: OnHitSaveDamageResolution
    uncanny_dodge_used: bool = False
    deflect_missiles_used: bool = False
    deflect_missiles_reduction: int = 0


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
    hp_buffer_before = defender.current_hp + defender.temporary_hp
    damage_roll, rolled_components = resolve_weapon_damage(
        attacker, attack, dice, critical, attack_mode, turn_key, bonus_damage=bonus_damage,
        target=defender, sneak_attack_ally_available=sneak_attack_ally_available,
    )
    save_damage = resolve_on_hit_save_damage(defender, attack, dice)
    save_component_present = save_damage.component is not None
    if save_component_present:
        rolled_components.append(save_damage.component)
    rolled_components, deflect_used, deflect_reduction = apply_deflect_missiles(
        defender,
        attack,
        rolled_components,
        dice,
    )
    rolled_components, uncanny_used = apply_uncanny_dodge(attacker, defender, rolled_components)
    damage_roll = aggregate_damage_components(rolled_components)
    applied_total, components = apply_damage_defenses(defender, rolled_components)
    damage_roll.total = applied_total
    applied_types = {part.damage_type for part in components if part.applied_total > 0}
    outcome = apply_damage(
        defender, applied_total, critical=critical, damage_types=applied_types,
        dice=dice, affected_states=affected_states,
    )
    effect = attack.on_hit_save_damage
    if defender.current_hp == 0 and save_damage_caused_zero(
        hp_buffer_before, applied_total, components, effect, save_component_present=save_component_present,
    ):
        assert effect is not None
        apply_zero_hp_save_damage_rider(defender, effect, turn_key, affected_states)
        outcome = "unconscious"
    return AttackHitDamageResolution(
        damage_roll=damage_roll,
        damage_components=components,
        damage_outcome=outcome,
        applied_total=applied_total,
        save_damage=save_damage,
        uncanny_dodge_used=uncanny_used,
        deflect_missiles_used=deflect_used,
        deflect_missiles_reduction=deflect_reduction,
    )
