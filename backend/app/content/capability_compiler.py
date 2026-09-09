from __future__ import annotations

import logging

from app.content.capability_attack_compiler import (
    UnsupportedCapabilityError,
    compile_attack,
    compile_persistent_effect,
)
from app.domain.actions import AttackActionDefinition, AttackActionSlot, SavingThrowAction
from app.domain.capabilities import CombatantDefinition, SaveCapabilityDefinition
from app.domain.capability_effects import ConditionEffectDefinition, GrappleEffectDefinition, ProneEffectDefinition
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def _compile_save(definition: SaveCapabilityDefinition) -> SavingThrowAction:
    damage = definition.damage
    controls = []
    modifiers: list[HitModifierEffect] = []
    if definition.grapple is not None:
        controls.append(compile_persistent_effect(definition.grapple))
    for effect in definition.effects:
        if isinstance(effect, HitModifierEffect):
            modifiers.append(effect)
        elif isinstance(effect, (GrappleEffectDefinition, ConditionEffectDefinition, ProneEffectDefinition)):
            controls.append(compile_persistent_effect(effect))
        else:
            raise UnsupportedCapabilityError(f"Unsupported save effect: {effect!r}")
    legacy_grapple = controls[0] if len(controls) == 1 and controls[0].grapple_escape_dc is not None else None
    return SavingThrowAction(
        id=definition.id,
        name=definition.name,
        save_ability=definition.save_ability,
        dc=definition.dc,
        range_ft=definition.range_ft,
        target_max_size=definition.target_max_size,
        damage_dice_count=damage.count if damage else 0,
        damage_dice_size=damage.size if damage else 6,
        damage_bonus=damage.bonus if damage else 0,
        damage_type=definition.damage_type.value if definition.damage_type else None,
        success_damage=definition.success_damage,
        persistent_effects=[] if legacy_grapple else controls,
        on_failure_modifier_effects=modifiers,
        grapple_escape_dc=legacy_grapple.grapple_escape_dc if legacy_grapple else None,
        restrains_while_grappled=legacy_grapple.restrains_while_grappled if legacy_grapple else False,
        resource_id=definition.resource_id,
        resource_cost=definition.resource_cost,
        animation=definition.animation,
    )


def _compile_attack_action(definition: CombatantDefinition) -> AttackActionDefinition | None:
    action = definition.attack_action
    if action is None:
        return None
    return AttackActionDefinition(
        id=action.id,
        name=action.name,
        is_attack_action=action.is_attack_action,
        slots=[
            AttackActionSlot(attack_ids=slot.attack_ids, save_action_ids=slot.save_action_ids)
            for slot in action.slots
        ],
    )


def compile_combatant(definition: CombatantDefinition) -> CombatantTemplate:
    try:
        if definition.unsupported_capabilities:
            blockers = ", ".join(sorted(definition.unsupported_capabilities))
            raise UnsupportedCapabilityError(
                f"{definition.id} requires unsupported capabilities: {blockers}"
            )
        attacks = [compile_attack(item) for item in definition.attacks]
        attack_by_id = {attack.id: attack for attack in attacks}
        primary = attack_by_id[definition.primary_attack_id]
        kwargs = definition.model_dump(exclude={
            "schema_version", "attacks", "primary_attack_id", "attack_action", "save_actions",
            "unsupported_capabilities", "movement_modes",
        })
        if definition.movement_modes is not None:
            kwargs["movement_modes"] = definition.movement_modes
        return CombatantTemplate(
            **kwargs,
            weapon_attack=primary,
            alternate_weapon_attacks=[attack for attack in attacks if attack.id != primary.id],
            attack_action=_compile_attack_action(definition),
            saving_throw_actions=[_compile_save(item) for item in definition.save_actions],
        )
    except UnsupportedCapabilityError:
        raise
    except Exception as exc:
        logger.exception("Failed to compile combat capability definition %s.", definition.id)
        raise RuntimeError(
            f"Combat capability definition {definition.id} could not be compiled."
        ) from exc
