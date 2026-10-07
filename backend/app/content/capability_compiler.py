from __future__ import annotations

import logging

from app.content.capability_attack_compiler import UnsupportedCapabilityError, compile_attack
from app.domain.actions import AttackActionDefinition, SavingThrowAction
from app.domain.capabilities import CombatantDefinition, SaveCapabilityDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def _compile_save(definition: SaveCapabilityDefinition) -> SavingThrowAction:
    damage = definition.damage
    grapple = definition.grapple
    return SavingThrowAction(
        id=definition.id,
        name=definition.name,
        action_cost=definition.action_cost,
        save_ability=definition.save_ability,
        dc=definition.dc,
        range_ft=definition.range_ft,
        target_max_size=definition.target_max_size or (grapple.max_target_size if grapple else None),
        area=definition.area,
        damage_dice_count=damage.count if damage else 0,
        damage_dice_size=damage.size if damage else 6,
        damage_bonus=damage.bonus if damage else 0,
        damage_type=definition.damage_type.value if definition.damage_type else None,
        success_damage=definition.success_damage,
        grapple_escape_dc=grapple.escape_dc if grapple else None,
        restrains_while_grappled=grapple.restrains if grapple else False,
        resource_id=definition.resource_id, resource_cost=definition.resource_cost,
        requires_no_active_grapple=definition.requires_no_active_grapple,
        magical_effect=definition.magical_effect, effect_tags=list(definition.effect_tags),
        failed_save_timed_effect=definition.failed_save_timed_effect,
        source_effect_immunity_on_success=definition.source_effect_immunity_on_success,
        failed_save_push_ft=definition.failed_save_push_ft,
        animation=definition.animation,
    )


def _compile_attack_action(definition: CombatantDefinition) -> AttackActionDefinition | None:
    try:
        action = definition.attack_action
        return AttackActionDefinition.model_validate(action.model_dump()) if action else None
    except Exception:
        logger.exception("Failed attack-action compilation for %s.", definition.id)
        raise


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
