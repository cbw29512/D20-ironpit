from __future__ import annotations

import logging

from app.content.capability_attack_control_compiler import (
    UnsupportedAttackControlError,
    compile_control,
    merge_controls,
)
from app.domain.actions import HitControlEffect
from app.domain.attachments import AttachmentEffectDefinition
from app.domain.capabilities import AttackCapabilityDefinition
from app.domain.capability_effects import (
    ConditionEffectDefinition,
    DamageEffectDefinition,
    GrappleEffectDefinition,
    MaxHpReductionEffectDefinition,
    ProneEffectDefinition,
)
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.models import ConditionalDamage, OnHitDamage, Weapon, WeaponAttack
from app.domain.weapons import AttachmentOnHit, MaxHpReductionOnHit

logger = logging.getLogger(__name__)


class UnsupportedCapabilityError(ValueError):
    pass


def compile_attack(definition: AttackCapabilityDefinition) -> WeaponAttack:
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
        on_hit: list[OnHitDamage] = []
        on_hit_modifiers: list[HitModifierEffect] = []
        conditional: list[ConditionalDamage] = []
        max_hp_reduction: MaxHpReductionOnHit | None = None
        attachment: AttachmentOnHit | None = None
        prone_size = None
        controls: list[HitControlEffect] = []
        for effect in definition.effects:
            if isinstance(effect, DamageEffectDefinition):
                if effect.trigger == "on_hit":
                    on_hit.append(OnHitDamage(
                        source=effect.source,
                        dice_count=effect.dice.count,
                        dice_size=effect.dice.size,
                        damage_bonus=effect.dice.bonus,
                        damage_type=effect.damage_type,
                    ))
                else:
                    conditional.append(ConditionalDamage(
                        trigger=effect.trigger,
                        mode=effect.mode,
                        dice_count=effect.dice.count,
                        dice_size=effect.dice.size,
                        damage_bonus=effect.dice.bonus,
                        damage_type=effect.damage_type,
                    ))
            elif isinstance(effect, ProneEffectDefinition):
                prone_size = effect.max_target_size
            elif isinstance(effect, HitModifierEffect):
                on_hit_modifiers.append(effect)
            elif isinstance(effect, MaxHpReductionEffectDefinition):
                if max_hp_reduction is not None:
                    raise UnsupportedCapabilityError("An attack supports at most one max-HP-reduction rider.")
                max_hp_reduction = MaxHpReductionOnHit(damage_type=effect.damage_type)
            elif isinstance(effect, AttachmentEffectDefinition):
                if attachment is not None:
                    raise UnsupportedCapabilityError("An attack supports at most one attachment rider.")
                attachment = AttachmentOnHit(
                    periodic_damage_count=effect.periodic_damage_count,
                    periodic_damage_size=effect.periodic_damage_size,
                    periodic_damage_bonus=effect.periodic_damage_bonus,
                    periodic_damage_type=effect.periodic_damage_type,
                    forbids_source_attack_ids=effect.forbids_source_attack_ids,
                    detachable_by_source_movement_ft=effect.detachable_by_source_movement_ft,
                    detachable_by_target_action=effect.detachable_by_target_action,
                    detachable_by_adjacent_action=effect.detachable_by_adjacent_action,
                )
            elif isinstance(effect, (GrappleEffectDefinition, ConditionEffectDefinition)):
                controls.append(compile_control(effect))
            else:
                raise UnsupportedCapabilityError(f"Unsupported attack effect: {effect!r}")
        return WeaponAttack(
            id=definition.id,
            weapon=weapon,
            attack_bonus=definition.attack_bonus,
            damage_bonus=damage.bonus if damage else 0,
            attack_ability=definition.attack_ability,
            attack_ability_modifier=definition.attack_ability_modifier,
            resource_id=definition.resource_id,
            resource_cost=definition.resource_cost,
            rage_eligible=definition.rage_eligible,
            fixed_damage=definition.fixed_damage,
            conditional_damage=conditional,
            conditional_attack_advantage=definition.conditional_attack_advantage,
            on_hit_damage=on_hit,
            on_hit_modifier_effects=on_hit_modifiers,
            max_hp_reduction_on_hit=max_hp_reduction,
            attachment_on_hit=attachment,
            knocks_prone_max_size=prone_size,
            control_effect=merge_controls(controls),
            charge_profile=definition.charge_profile,
            push_target_away_ft=definition.push_target_away_ft,
            push_target_max_size=definition.push_target_max_size,
            pull_target_toward_ft=definition.pull_target_toward_ft,
            pull_target_max_size=definition.pull_target_max_size,
            forbid_target_grappled_by_self=definition.forbid_target_grappled_by_self,
        )
    except UnsupportedCapabilityError:
        raise
    except UnsupportedAttackControlError as exc:
        logger.error("Unsupported attack control composition for %s: %s", definition.id, exc)
        raise UnsupportedCapabilityError(str(exc)) from exc
    except Exception:
        logger.exception("Failed to compile attack capability %s.", definition.id)
        raise
