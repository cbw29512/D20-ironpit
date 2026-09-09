from __future__ import annotations

from app.domain.capability_attacks import AttackCapabilityDefinition, SaveCapabilityDefinition
from app.domain.combat_ir import AttackRollResolutionIR, CombatActionIR, SavingThrowResolutionIR


def _resource_parts(action: CombatActionIR) -> tuple[str | None, int]:
    if not action.resource_costs:
        return None, 1
    if len(action.resource_costs) != 1:
        raise ValueError(f"Legacy capability {action.id} cannot represent multiple resource costs.")
    cost = action.resource_costs[0]
    if cost.mode != "per_use":
        raise ValueError(f"Legacy capability {action.id} cannot represent {cost.mode} resource costs.")
    return cost.resource_id, cost.amount


def attack_ir_to_capability(action: CombatActionIR) -> AttackCapabilityDefinition:
    if not isinstance(action.resolution, AttackRollResolutionIR):
        raise ValueError(f"Combat action {action.id} is not an attack-roll action.")
    if action.primary_damage is None:
        raise ValueError(f"Attack-roll action {action.id} is missing primary damage.")
    resource_id, resource_cost = _resource_parts(action)
    resolution = action.resolution
    return AttackCapabilityDefinition(
        id=action.id,
        name=action.name,
        weapon_id=resolution.weapon_id,
        attack_kind=resolution.attack_kind,
        attack_bonus=resolution.attack_bonus,
        damage=action.primary_damage.dice,
        fixed_damage=action.primary_damage.fixed_damage,
        damage_type=action.primary_damage.damage_type,
        animation=action.animation,
        reach_ft=resolution.reach_ft,
        normal_range_ft=resolution.normal_range_ft,
        long_range_ft=resolution.long_range_ft,
        projectile=resolution.projectile,
        mastery_property=resolution.mastery_property,
        light=resolution.light,
        finesse=resolution.finesse,
        heavy=resolution.heavy,
        two_handed=resolution.two_handed,
        versatile=resolution.versatile,
        attack_ability=resolution.attack_ability,
        attack_ability_modifier=resolution.attack_ability_modifier,
        rage_eligible=resolution.rage_eligible,
        conditional_attack_modifiers=list(resolution.conditional_attack_modifiers),
        effects=list(action.effects),
        forbid_target_grappled_by_self=resolution.forbid_target_grappled_by_self,
        resource_id=resource_id,
        resource_cost=resource_cost,
    )


def save_ir_to_capability(action: CombatActionIR) -> SaveCapabilityDefinition:
    if not isinstance(action.resolution, SavingThrowResolutionIR):
        raise ValueError(f"Combat action {action.id} is not a saving-throw action.")
    if len(action.effects) > 1:
        raise ValueError(f"Current save compatibility adapter accepts one control effect: {action.id}.")
    failure_control = action.effects[0] if action.effects else None
    if failure_control is not None and failure_control.kind not in {"grapple", "condition", "forced_movement"}:
        raise ValueError(f"Unsupported save compatibility effect {failure_control.kind}: {action.id}.")
    resource_id, resource_cost = _resource_parts(action)
    damage = action.primary_damage
    return SaveCapabilityDefinition(
        id=action.id,
        name=action.name,
        save_ability=action.resolution.save_ability,
        dc=action.resolution.dc,
        range_ft=action.targeting.range_ft,
        area=action.targeting.area,
        target_max_size=action.targeting.max_target_size,
        damage=None if damage is None else damage.dice,
        damage_type=None if damage is None else damage.damage_type,
        success_damage=action.resolution.success_damage,
        magical_effect=action.resolution.magical_effect,
        failure_control=failure_control,
        resource_id=resource_id,
        resource_cost=resource_cost,
        animation=action.animation,
    )
