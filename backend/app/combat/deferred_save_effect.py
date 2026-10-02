from __future__ import annotations

from dataclasses import dataclass
import logging

from app.domain.encounters import EncounterSetup
from app.domain.models import CombatantState, WeaponAttack
from app.domain.runtime import DeferredEffectState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeferredEffectArmResult:
    source_id: str
    source_name: str
    target_id: str
    resource_remaining: int
    armed_round: int


def arm_deferred_save_effect(
    attacker: CombatantState,
    defender: CombatantState,
    target_id: str,
    attack: WeaponAttack,
    round_number: int,
) -> DeferredEffectArmResult | None:
    """Arm one declarative deferred effect after a qualifying successful hit."""
    try:
        rule = attacker.template.progression_features.deferred_save_effect
        if rule is None or attack.weapon.id not in rule.trigger_weapon_ids:
            return None
        if defender.is_dead or not defender.is_alive or defender.current_hp <= 0:
            return None
        active = [item for item in attacker.deferred_effects if item.source_id == rule.source_id]
        if any(item.target_id == target_id for item in active):
            return None
        if len(active) >= rule.max_active_targets:
            if not rule.allow_harmless_end_on_rearm:
                return None
            attacker.deferred_effects = [
                item for item in attacker.deferred_effects if item.source_id != rule.source_id
            ]
        resource = next((item for item in attacker.resources if item.id == rule.resource_id), None)
        if resource is None:
            raise ValueError(
                f"Deferred effect {rule.source_id} references missing resource {rule.resource_id}."
            )
        if resource.current_uses < rule.resource_cost:
            return None
        resource.current_uses -= rule.resource_cost
        attacker.deferred_effects.append(
            DeferredEffectState(
                source_id=rule.source_id,
                target_id=target_id,
                armed_round=round_number,
            )
        )
        return DeferredEffectArmResult(
            source_id=rule.source_id,
            source_name=rule.source_name,
            target_id=target_id,
            resource_remaining=resource.current_uses,
            armed_round=round_number,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to arm deferred save effect for %s.", attacker.template.name)
        raise RuntimeError("Deferred save effect could not be armed.") from exc


def cleanup_deferred_effects(setup: EncounterSetup) -> None:
    """Remove armed marks whose target no longer exists or can no longer be affected."""
    try:
        members = [*setup.heroes, *setup.monsters]
        by_id = {member.combatant_id: member for member in members}
        for source in members:
            source.state.deferred_effects = [
                mark
                for mark in source.state.deferred_effects
                if (
                    (target := by_id.get(mark.target_id)) is not None
                    and target.state.is_alive
                    and not target.state.is_dead
                    and target.state.current_hp > 0
                )
            ]
    except Exception as exc:
        logger.exception("Failed deferred-effect lifecycle cleanup.")
        raise RuntimeError("Deferred-effect lifecycle cleanup failed.") from exc


from app.combat.deferred_save_effect_activation import (  # noqa: E402
    deferred_save_effect_candidate,
    resolve_deferred_save_effect,
)

__all__ = [
    "DeferredEffectArmResult",
    "arm_deferred_save_effect",
    "cleanup_deferred_effects",
    "deferred_save_effect_candidate",
    "resolve_deferred_save_effect",
]
