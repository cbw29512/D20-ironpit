from __future__ import annotations

import logging

from app.domain.models import AttackRollEffect, AttackRollEffectKind, CombatantState, Weapon

logger = logging.getLogger(__name__)
SAP_MASTERY = "sap"
VEX_MASTERY = "vex"


def _applies_to_target(effect: AttackRollEffect, target_actor_id: str | None) -> bool:
    try:
        return effect.target_actor_id is None or effect.target_actor_id == target_actor_id
    except Exception as exc:
        logger.exception("Failed to match attack-roll effect target.")
        raise RuntimeError("Attack-roll effect target could not be matched.") from exc


def resolve_attack_roll_effect_sources(
    state: CombatantState,
    target_actor_id: str | None = None,
) -> tuple[int, int]:
    try:
        applicable = [
            effect for effect in state.attack_roll_effects
            if _applies_to_target(effect, target_actor_id)
        ]
        advantage = sum(effect.kind is AttackRollEffectKind.ADVANTAGE for effect in applicable)
        disadvantage = sum(effect.kind is AttackRollEffectKind.DISADVANTAGE for effect in applicable)
        return advantage, disadvantage
    except Exception as exc:
        logger.exception("Failed to resolve attack-roll effects for %s.", state.template.name)
        raise RuntimeError("Attack-roll effects could not be resolved.") from exc


def consume_attack_roll_effects(
    state: CombatantState,
    target_actor_id: str | None = None,
) -> None:
    try:
        state.attack_roll_effects = [
            effect
            for effect in state.attack_roll_effects
            if not (
                effect.consume_on_attack
                and _applies_to_target(effect, target_actor_id)
            )
        ]
    except Exception as exc:
        logger.exception("Failed to consume attack-roll effects for %s.", state.template.name)
        raise RuntimeError("Attack-roll effects could not be consumed.") from exc


def _apply_sap(attacker: CombatantState, defender: CombatantState) -> str:
    defender.attack_roll_effects = [
        effect for effect in defender.attack_roll_effects
        if not (effect.id == SAP_MASTERY and effect.source_actor_id == attacker.template.id)
    ]
    defender.attack_roll_effects.append(
        AttackRollEffect(
            id=SAP_MASTERY,
            source_actor_id=attacker.template.id,
            kind=AttackRollEffectKind.DISADVANTAGE,
        )
    )
    return SAP_MASTERY


def _apply_vex(attacker: CombatantState, defender: CombatantState) -> str:
    attacker.attack_roll_effects = [
        effect for effect in attacker.attack_roll_effects
        if not (effect.id == VEX_MASTERY and effect.target_actor_id == defender.template.id)
    ]
    attacker.attack_roll_effects.append(
        AttackRollEffect(
            id=VEX_MASTERY,
            source_actor_id=attacker.template.id,
            target_actor_id=defender.template.id,
            kind=AttackRollEffectKind.ADVANTAGE,
            expires_at_start_of_source_turn=False,
            source_turns_remaining=2,
        )
    )
    return VEX_MASTERY


def apply_weapon_mastery_on_hit(
    attacker: CombatantState,
    defender: CombatantState,
    weapon: Weapon,
    damage_dealt: bool = True,
) -> str | None:
    try:
        if weapon.id not in attacker.template.weapon_masteries:
            return None
        if weapon.mastery_property == SAP_MASTERY:
            return _apply_sap(attacker, defender)
        if weapon.mastery_property == VEX_MASTERY and damage_dealt:
            return _apply_vex(attacker, defender)
        return None
    except Exception as exc:
        logger.exception(
            "Failed to apply weapon mastery for %s with %s.",
            attacker.template.name,
            weapon.name,
        )
        raise RuntimeError("Weapon mastery effect could not be applied.") from exc
