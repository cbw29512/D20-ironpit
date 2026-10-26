from __future__ import annotations

import logging

from app.content.capability_attack_effect_compiler import compile_attack_effects
from app.content.capability_charge_compiler import compile_charge
from app.content.capability_errors import UnsupportedCapabilityError
from app.domain.capabilities import AttackCapabilityDefinition
from app.domain.models import Weapon, WeaponAttack

logger = logging.getLogger(__name__)


def compile_attack(definition: AttackCapabilityDefinition) -> WeaponAttack:
    """Compile one declarative attack without source-name dispatch."""
    try:
        damage = definition.damage
        weapon = Weapon(
            id=definition.weapon_id or definition.id,
            name=definition.name,
            attack_kind=definition.attack_kind,
            dice_count=damage.count if damage else 0,
            dice_size=damage.size if damage else 2,
            damage_type=definition.damage_type,
            animation=definition.animation,
            reach_ft=definition.reach_ft,
            normal_range_ft=definition.normal_range_ft,
            long_range_ft=definition.long_range_ft,
            projectile=definition.projectile,
            mastery_property=definition.mastery_property,
            light=definition.light,
            finesse=definition.finesse,
            heavy=definition.heavy,
            two_handed=definition.two_handed,
            versatile=definition.versatile,
        )
        effects = compile_attack_effects(definition)
        return WeaponAttack(
            id=definition.id,
            weapon=weapon,
            resource_id=definition.resource_id,
            resource_cost=definition.resource_cost,
            attack_bonus=definition.attack_bonus,
            damage_bonus=damage.bonus if damage else 0,
            attack_ability=definition.attack_ability,
            attack_ability_modifier=definition.attack_ability_modifier,
            rage_eligible=definition.rage_eligible,
            sneak_attack_eligible=definition.sneak_attack_eligible,
            fixed_damage=definition.fixed_damage,
            conditional_damage=effects.conditional,
            conditional_attack_advantage=definition.conditional_attack_advantage,
            on_hit_damage=effects.on_hit,
            on_hit_save_damage=effects.on_hit_save_damage,
            on_hit_condition_save=effects.on_hit_save,
            on_hit_ongoing_hp_loss=effects.on_hit_hp_loss,
            on_hit_maximum_hp_save=effects.on_hit_maximum_hp_save,
            on_hit_ability_score_reduction=effects.on_hit_ability_score_reduction,
            on_hit_contested_movement=effects.on_hit_contested_movement,
            on_hit_modifier_effects=effects.on_hit_modifiers,
            charge_profile=compile_charge(definition.charge_profile),
            knocks_prone_max_size=effects.prone_size,
            control_effect=effects.control,
            forbid_target_grappled_by_self=definition.forbid_target_grappled_by_self,
            grapple_target_policy=definition.grapple_target_policy,
            unavailable_reason=definition.unavailable_reason,
            damage_source_qualifiers=list(definition.damage_source_qualifiers),
        )
    except Exception:
        logger.exception("Failed to compile attack capability %s.", definition.id)
        raise
