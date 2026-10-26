from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.dice import DiceProvider
from app.combat.save_damage_components import resolve_save_damage_components
from app.combat.zero_hp import apply_damage, reduce_to_zero_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageRollComponent, DiceRoll, SavingThrowAction
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SaveDamageResult:
    damage_roll: DiceRoll | None
    damage_components: list[DamageRollComponent]
    damage_outcome: str | None


def resolve_save_damage(
    target: EncounterCombatant,
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
    *,
    shared_damage_rolls: list[int] | list[list[int]] | None = None,
    affected_states: list[CombatantState] | None = None,
    setup: EncounterSetup | None = None,
) -> SaveDamageResult:
    try:
        total, rolled, components = resolve_save_damage_components(
            target.state, action, dice, succeeded, shared_damage_rolls,
        )
        damage_roll = None
        damage_outcome = None
        if rolled:
            damage_roll = DiceRoll(
                notation=" + ".join(item.notation for item in rolled),
                rolls=[roll for item in rolled for roll in item.rolls],
                modifier=sum(item.modifier for item in rolled),
                total=total,
            )
        if total:
            applied_types = {
                part.damage_type
                for part in components
                if part.applied_total > 0
            }
            incoming = total
            if action.minimum_remaining_hp:
                total = min(
                    total,
                    max(0, target.state.current_hp - action.minimum_remaining_hp),
                )
            damage_outcome = apply_damage(
                target.state,
                total,
                damage_types=applied_types,
                dice=dice,
                affected_states=affected_states,
                setup=setup,
                damage_components=components,
            )
            end_rage_if_incapacitated(target.state)
            if (
                not succeeded
                and action.reduce_hit_point_maximum_on_failed_save
                and incoming
            ):
                from app.combat.restoration_riders import (
                    apply_hit_point_maximum_reduction,
                )
                apply_hit_point_maximum_reduction(target, incoming)
        if not succeeded and action.failure_sets_zero_hp:
            reduce_to_zero_hit_points(
                target.state,
                dice=dice,
                affected_states=affected_states,
            )
        return SaveDamageResult(
            damage_roll=damage_roll,
            damage_components=components,
            damage_outcome=damage_outcome,
        )
    except Exception:
        logger.exception(
            "Failed to resolve save damage for %s against %s.",
            action.id,
            target.combatant_id,
        )
        raise
