from __future__ import annotations

import logging

from app.domain.actions import AttackActionDefinition, AttackActionSlot, HitControlEffect, SavingThrowAction
from app.domain.capabilities import AttackCapabilityDefinition, CombatantDefinition, SaveCapabilityDefinition
from app.domain.capability_effects import ConditionEffectDefinition, DamageEffectDefinition, GrappleEffectDefinition, ProneEffectDefinition
from app.domain.models import CombatantTemplate, ConditionalDamage, OnHitDamage, Weapon, WeaponAttack

logger = logging.getLogger(__name__)


class UnsupportedCapabilityError(ValueError):
    pass


def _compile_control(effect: GrappleEffectDefinition | ConditionEffectDefinition) -> HitControlEffect:
    if isinstance(effect, GrappleEffectDefinition):
        return HitControlEffect(
            max_target_size=effect.max_target_size,
            grapple_escape_dc=effect.escape_dc,
            restrains_while_grappled=effect.restrains,
        )
    return HitControlEffect(
        max_target_size=effect.max_target_size,
        condition_id=effect.condition,
        expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
        expiry_timing=effect.expiry_timing,
        repeat_save_ability=effect.repeat_save_ability,
        repeat_save_dc=effect.repeat_save_dc,
        repeat_save_timing=effect.repeat_save_timing,
        allowed_removal_action_ids=effect.allowed_removal_action_ids,
    )


def _compile_attack(definition: AttackCapabilityDefinition) -> WeaponAttack:
    dice_count = definition.damage.count if definition.damage else 0
    dice_size = definition.damage.size if definition.damage else 2
    damage_bonus = definition.damage.bonus if definition.damage else 0
    weapon = Weapon(
        id=definition.weapon_id or definition.id,
        name=definition.name,
        attack_kind=definition.attack_kind,
        dice_count=dice_count,
        dice_size=dice_size,
        damage_type=definition.damage_type,
        animation=definition.animation,
        reach_ft=definition.reach_ft,
        normal_range_ft=definition.normal_range_ft,
        long_range_ft=definition.long_range_ft,
        projectile=definition.projectile,
        mastery_property=definition.mastery_property,
        light=definition.light,
    )
    on_hit: list[OnHitDamage] = []
    conditional: list[ConditionalDamage] = []
    prone_size = None
    control = None
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
        elif isinstance(effect, (GrappleEffectDefinition, ConditionEffectDefinition)):
            control = _compile_control(effect)
        else:
            raise UnsupportedCapabilityError(f"Unsupported attack effect: {effect!r}")
    return WeaponAttack(
        id=definition.id,
        weapon=weapon,
        attack_bonus=definition.attack_bonus,
        damage_bonus=damage_bonus,
        attack_ability=definition.attack_ability,
        attack_ability_modifier=definition.attack_ability_modifier,
        rage_eligible=definition.rage_eligible,
        fixed_damage=definition.fixed_damage,
        conditional_damage=conditional,
        on_hit_damage=on_hit,
        knocks_prone_max_size=prone_size,
        control_effect=control,
        forbid_target_grappled_by_self=definition.forbid_target_grappled_by_self,
    )


def _compile_save(definition: SaveCapabilityDefinition) -> SavingThrowAction:
    damage = definition.damage
    grapple = definition.grapple
    return SavingThrowAction(
        id=definition.id,
        name=definition.name,
        save_ability=definition.save_ability,
        dc=definition.dc,
        range_ft=definition.range_ft,
        target_max_size=definition.target_max_size or (grapple.max_target_size if grapple else None),
        damage_dice_count=damage.count if damage else 0,
        damage_dice_size=damage.size if damage else 6,
        damage_bonus=damage.bonus if damage else 0,
        damage_type=definition.damage_type.value if definition.damage_type else None,
        success_damage=definition.success_damage,
        grapple_escape_dc=grapple.escape_dc if grapple else None,
        restrains_while_grappled=grapple.restrains if grapple else False,
        animation=definition.animation,
    )


def compile_combatant(definition: CombatantDefinition) -> CombatantTemplate:
    try:
        if definition.unsupported_capabilities:
            blockers = ", ".join(sorted(definition.unsupported_capabilities))
            raise UnsupportedCapabilityError(f"{definition.id} requires unsupported capabilities: {blockers}")
        attacks = [_compile_attack(item) for item in definition.attacks]
        attack_by_id = {attack.id: attack for attack in attacks}
        primary = attack_by_id[definition.primary_attack_id]
        saves = [_compile_save(item) for item in definition.save_actions]
        attack_action = None
        if definition.attack_action:
            attack_action = AttackActionDefinition(
                id=definition.attack_action.id,
                name=definition.attack_action.name,
                is_attack_action=definition.attack_action.is_attack_action,
                slots=[AttackActionSlot(attack_ids=slot.attack_ids, save_action_ids=slot.save_action_ids)
                       for slot in definition.attack_action.slots],
            )
        kwargs = definition.model_dump(exclude={"schema_version", "attacks", "primary_attack_id", "attack_action", "save_actions", "unsupported_capabilities", "movement_modes"})
        if definition.movement_modes is not None:
            kwargs["movement_modes"] = definition.movement_modes
        return CombatantTemplate(
            **kwargs,
            weapon_attack=primary,
            alternate_weapon_attacks=[attack for attack in attacks if attack.id != primary.id],
            attack_action=attack_action,
            saving_throw_actions=saves,
        )
    except UnsupportedCapabilityError:
        raise
    except Exception as exc:
        logger.exception("Failed to compile combat capability definition %s.", definition.id)
        raise RuntimeError(f"Combat capability definition {definition.id} could not be compiled.") from exc
