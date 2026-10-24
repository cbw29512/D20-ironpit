from __future__ import annotations

from dataclasses import dataclass
import logging

from app.content.capability_errors import UnsupportedCapabilityError
from app.content.capability_attack_control_compiler import compile_attack_control
from app.domain.capabilities import AttackCapabilityDefinition
from app.domain.capability_effects import (
    AbilityScoreReductionEffectDefinition,
    ConditionEffectDefinition,
    ContestedMovementEffectDefinition,
    DamageEffectDefinition,
    GrappleEffectDefinition,
    OngoingHpLossEffectDefinition,
    ProneEffectDefinition,
    SaveConditionEffectDefinition,
    SaveDamageEffectDefinition,
    SaveMaximumHpReductionEffectDefinition,
)
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.models import ConditionalDamage, OnHitDamage
from app.domain.size import CreatureSize
from app.domain.weapons import (
    OnHitAbilityScoreReduction,
    OnHitConditionSave,
    OnHitContestedMovement,
    OnHitMaximumHpSave,
    OnHitOngoingHpLoss,
    OnHitSaveDamage,
)

logger = logging.getLogger(__name__)


@dataclass
class CompiledAttackEffects:
    on_hit: list[OnHitDamage]
    on_hit_modifiers: list[HitModifierEffect]
    conditional: list[ConditionalDamage]
    prone_size: CreatureSize | None
    control: HitControlEffect | None
    on_hit_save: OnHitConditionSave | None
    on_hit_hp_loss: OnHitOngoingHpLoss | None
    on_hit_save_damage: OnHitSaveDamage | None
    on_hit_maximum_hp_save: OnHitMaximumHpSave | None
    on_hit_ability_score_reduction: OnHitAbilityScoreReduction | None
    on_hit_contested_movement: OnHitContestedMovement | None



def compile_attack_effects(definition: AttackCapabilityDefinition) -> CompiledAttackEffects:
    """Compile source-neutral attack effects independently from weapon construction."""
    try:
        result = CompiledAttackEffects([], [], [], None, None, None, None, None, None, None, None)
        for effect in definition.effects:
            if isinstance(effect, DamageEffectDefinition):
                if effect.trigger == "on_hit":
                    result.on_hit.append(OnHitDamage(
                        source=effect.source, dice_count=effect.dice.count,
                        dice_size=effect.dice.size, damage_bonus=effect.dice.bonus,
                        damage_type=effect.damage_type,
                    ))
                else:
                    result.conditional.append(ConditionalDamage(
                        trigger=effect.trigger,
                        source_name=effect.source if effect.trigger == "round1_initiative_lead" else None,
                        mode=effect.mode, dice_count=effect.dice.count,
                        dice_size=effect.dice.size, damage_bonus=effect.dice.bonus,
                        damage_type=effect.damage_type,
                    ))
            elif isinstance(effect, SaveDamageEffectDefinition):
                result.on_hit_save_damage = OnHitSaveDamage(
                    source=effect.source, save_ability=effect.save_ability, dc=effect.dc,
                    dice_count=effect.dice.count, dice_size=effect.dice.size,
                    damage_bonus=effect.dice.bonus, damage_type=effect.damage_type,
                    success_damage=effect.success_damage, zero_hp_rider=effect.zero_hp_rider,
                )
            elif isinstance(effect, AbilityScoreReductionEffectDefinition):
                result.on_hit_ability_score_reduction = OnHitAbilityScoreReduction(
                    source=effect.source, ability=effect.ability,
                    dice_count=effect.dice.count, dice_size=effect.dice.size,
                )
            elif isinstance(effect, ContestedMovementEffectDefinition):
                result.on_hit_contested_movement = OnHitContestedMovement(
                    source_ability=effect.source_ability, target_ability=effect.target_ability,
                    max_target_size=effect.max_target_size, distance_ft=effect.distance_ft,
                    direction=effect.direction,
                )
            elif isinstance(effect, SaveMaximumHpReductionEffectDefinition):
                result.on_hit_maximum_hp_save = OnHitMaximumHpSave(
                    save_ability=effect.save_ability, dc=effect.dc, reduction=effect.reduction,
                    zero_max_hp_kills=effect.zero_max_hp_kills,
                )
            elif isinstance(effect, ProneEffectDefinition):
                result.prone_size = effect.max_target_size
            elif isinstance(effect, SaveConditionEffectDefinition):
                result.on_hit_save = OnHitConditionSave(
                    save_ability=effect.save_ability, dc=effect.dc,
                    condition_id=effect.condition, max_target_size=effect.max_target_size,
                    duration_rounds=effect.duration_rounds,
                    repeat_save_timing=effect.repeat_save_timing,
                    repeat_save_failure_condition_id=effect.repeat_save_failure_condition,
                    failure_push_ft=effect.failure_push_ft,
                    cannot_regain_hit_points=effect.cannot_regain_hit_points,
                    start_of_turn_damage_dice_count=effect.start_of_turn_damage_dice_count,
                    start_of_turn_damage_dice_size=effect.start_of_turn_damage_dice_size,
                    start_of_turn_damage_type=effect.start_of_turn_damage_type,
                    failure_margin_escalation=effect.failure_margin_escalation,
                    excluded_creature_types=list(effect.excluded_creature_types),
                    excluded_creature_subtypes=list(effect.excluded_creature_subtypes),
                )
            elif isinstance(effect, OngoingHpLossEffectDefinition):
                result.on_hit_hp_loss = OnHitOngoingHpLoss(
                    effect_id=effect.effect_id, source_name=effect.source_name,
                    save_ability=effect.save_ability, dc=effect.dc,
                    dice_count=effect.dice_count, dice_size=effect.dice_size,
                    excluded_creature_types=list(effect.excluded_creature_types),
                    stacks_on_reapply=effect.stacks_on_reapply,
                    ends_on_magical_healing=effect.ends_on_magical_healing,
                )
            elif isinstance(effect, HitModifierEffect):
                result.on_hit_modifiers.append(effect)
            elif isinstance(effect, (GrappleEffectDefinition, ConditionEffectDefinition)):
                result.control = compile_attack_control(effect)
            else:
                raise UnsupportedCapabilityError(f"Unsupported attack effect: {effect!r}")
        return result
    except Exception:
        logger.exception("Failed to compile attack effects for %s.", definition.id)
        raise
