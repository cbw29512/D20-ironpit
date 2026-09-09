from __future__ import annotations

from app.domain.capability_attacks import AttackCapabilityDefinition, SaveCapabilityDefinition
from app.domain.combat_ir import (
    AttackRollResolutionIR,
    CombatActionIR,
    PrimaryDamageIR,
    ResourceCostIR,
    SavingThrowResolutionIR,
    TargetingIR,
)
from app.domain.weapons import WeaponAttackKind


def _resources(resource_id: str | None, amount: int) -> list[ResourceCostIR]:
    if resource_id is None:
        return []
    return [ResourceCostIR(resource_id=resource_id, amount=amount)]


def attack_capability_to_ir(attack: AttackCapabilityDefinition) -> CombatActionIR:
    range_ft = attack.reach_ft
    if attack.attack_kind is WeaponAttackKind.RANGED:
        if attack.normal_range_ft is None:
            raise ValueError(f"Ranged attack {attack.id} is missing normal range.")
        range_ft = attack.normal_range_ft
    return CombatActionIR(
        id=attack.id,
        name=attack.name,
        targeting=TargetingIR(mode="single", range_ft=range_ft),
        resolution=AttackRollResolutionIR(
            attack_kind=attack.attack_kind,
            attack_bonus=attack.attack_bonus,
            weapon_id=attack.weapon_id,
            reach_ft=attack.reach_ft,
            normal_range_ft=attack.normal_range_ft,
            long_range_ft=attack.long_range_ft,
            projectile=attack.projectile,
            mastery_property=attack.mastery_property,
            light=attack.light,
            finesse=attack.finesse,
            heavy=attack.heavy,
            two_handed=attack.two_handed,
            versatile=attack.versatile,
            attack_ability=attack.attack_ability,
            attack_ability_modifier=attack.attack_ability_modifier,
            rage_eligible=attack.rage_eligible,
            conditional_attack_modifiers=list(attack.conditional_attack_modifiers),
            forbid_target_grappled_by_self=attack.forbid_target_grappled_by_self,
        ),
        primary_damage=PrimaryDamageIR(
            dice=attack.damage,
            fixed_damage=attack.fixed_damage,
            damage_type=attack.damage_type,
        ),
        effects=list(attack.effects),
        resource_costs=_resources(attack.resource_id, attack.resource_cost),
        animation=attack.animation,
    )


def save_capability_to_ir(action: SaveCapabilityDefinition) -> CombatActionIR:
    effects = []
    if action.failure_control is not None:
        effects.append(action.failure_control)
    elif action.grapple is not None:
        effects.append(action.grapple)
    primary_damage = None
    if action.damage is not None:
        if action.damage_type is None:
            raise ValueError(f"Save action {action.id} has damage dice without a damage type.")
        primary_damage = PrimaryDamageIR(dice=action.damage, damage_type=action.damage_type)
    return CombatActionIR(
        id=action.id,
        name=action.name,
        targeting=TargetingIR(
            mode="area" if action.area is not None else "single",
            range_ft=action.range_ft,
            area=action.area,
            max_target_size=action.target_max_size,
        ),
        resolution=SavingThrowResolutionIR(
            save_ability=action.save_ability,
            dc=action.dc,
            success_damage=action.success_damage,
            magical_effect=action.magical_effect,
        ),
        primary_damage=primary_damage,
        effects=effects,
        resource_costs=_resources(action.resource_id, action.resource_cost),
        animation=action.animation,
    )
