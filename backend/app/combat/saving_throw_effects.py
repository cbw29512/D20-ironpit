from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.failed_save_timed_apply import apply_failed_save_timed_effect
from app.combat.forced_movement import push_straight_away
from app.combat.grapple import apply_grapple
from app.combat.source_effect_immunity import (
    grant_shared_source_effect_immunities,
    grant_source_effect_immunity,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DiceRoll, SavingThrowAction
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SaveEffectResult:
    applied_conditions: list[str]
    pushed_ft: int


def apply_save_effects(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    succeeded: bool,
    save_roll: DiceRoll | None,
    round_number: int,
    *,
    affected_states: list[CombatantState] | None = None,
    setup: EncounterSetup | None = None,
) -> SaveEffectResult:
    try:
        applied_conditions: list[str] = []
        if succeeded and action.source_effect_immunity_on_success:
            grant_source_effect_immunity(
                target.state,
                action.id,
                actor.combatant_id,
                round_number,
                source_template=actor.state.template,
                source_is_magical=action.magical_effect,
            )
        if succeeded and action.source_effect_immunity_keys_on_success:
            grant_shared_source_effect_immunities(
                target.state,
                action.source_effect_immunity_keys_on_success,
                actor.combatant_id,
                round_number,
                source_template=actor.state.template,
                source_is_magical=action.magical_effect,
            )
        if not succeeded and target.state.is_alive and not target.state.is_dead:
            applied = apply_failed_save_timed_effect(
                target,
                actor,
                action,
                round_number,
                affected_states,
                setup,
                save_total=save_roll.total if save_roll is not None else None,
            )
            if isinstance(applied, str):
                applied_conditions.append(applied)
            elif applied:
                applied_conditions.extend(applied)
        if (
            not succeeded
            and target.state.is_alive
            and not target.state.is_dead
            and action.grapple_escape_dc is not None
        ):
            applied_conditions = apply_grapple(
                target.state,
                actor.combatant_id,
                action.grapple_escape_dc,
                action.range_ft,
                restrains=action.restrains_while_grappled,
                source_is_magical=action.magical_effect,
            )
        pushed_ft = 0
        if (
            not succeeded
            and target.state.is_alive
            and not target.state.is_dead
            and action.failed_save_push_ft
        ):
            if setup is None:
                raise ValueError(
                    f"{action.name} forced movement requires encounter setup."
                )
            pushed_ft = push_straight_away(
                target,
                actor,
                setup,
                action.failed_save_push_ft,
                round_number=round_number,
            )
        return SaveEffectResult(
            applied_conditions=applied_conditions,
            pushed_ft=pushed_ft,
        )
    except Exception:
        logger.exception(
            "Failed to apply save effects for %s against %s.",
            action.id,
            target.combatant_id,
        )
        raise
