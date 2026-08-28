from __future__ import annotations

import logging

from app.domain.models import AttackRollEffect, AttackRollEffectKind, CombatantState, Weapon

logger = logging.getLogger(__name__)
SAP_MASTERY = "sap"


def resolve_attack_roll_effect_sources(state: CombatantState) -> tuple[int, int]:
    """Return active Advantage and Disadvantage source counts for the next attack roll."""
    try:
        advantage = sum(
            effect.kind is AttackRollEffectKind.ADVANTAGE
            for effect in state.attack_roll_effects
        )
        disadvantage = sum(
            effect.kind is AttackRollEffectKind.DISADVANTAGE
            for effect in state.attack_roll_effects
        )
        return advantage, disadvantage
    except Exception as exc:
        logger.exception("Failed to resolve attack-roll effects for %s.", state.template.name)
        raise RuntimeError("Attack-roll effects could not be resolved.") from exc


def consume_attack_roll_effects(state: CombatantState) -> None:
    """Consume effects that explicitly end after the creature makes its next attack roll."""
    try:
        state.attack_roll_effects = [
            effect for effect in state.attack_roll_effects if not effect.consume_on_attack
        ]
    except Exception as exc:
        logger.exception("Failed to consume attack-roll effects for %s.", state.template.name)
        raise RuntimeError("Attack-roll effects could not be consumed.") from exc


def apply_weapon_mastery_on_hit(
    attacker: CombatantState,
    defender: CombatantState,
    weapon: Weapon,
) -> str | None:
    """Apply supported mastery effects only when the attacker has mastered that weapon kind."""
    try:
        if weapon.id not in attacker.template.weapon_masteries:
            return None
        if weapon.mastery_property != SAP_MASTERY:
            return None

        defender.attack_roll_effects = [
            effect
            for effect in defender.attack_roll_effects
            if not (
                effect.id == SAP_MASTERY
                and effect.source_actor_id == attacker.template.id
            )
        ]
        defender.attack_roll_effects.append(
            AttackRollEffect(
                id=SAP_MASTERY,
                source_actor_id=attacker.template.id,
                kind=AttackRollEffectKind.DISADVANTAGE,
                consume_on_attack=True,
                expires_at_start_of_source_turn=True,
            )
        )
        return SAP_MASTERY
    except Exception as exc:
        logger.exception(
            "Failed to apply weapon mastery for %s with %s.",
            attacker.template.name,
            weapon.name,
        )
        raise RuntimeError("Weapon mastery effect could not be applied.") from exc
