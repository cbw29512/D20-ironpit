from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageType
from app.domain.traits import CombatTrait


logger = logging.getLogger(__name__)

def resolve_undead_fortitude(
    state: CombatantState,
    damage_taken: int,
    damage_types: set[DamageType],
    *,
    critical: bool,
    dice: DiceProvider | None,
) -> bool:
    """Resolve SRD 5.2.1 Undead Fortitude after lethal damage reaches 0 HP."""
    if CombatTrait.UNDEAD_FORTITUDE not in state.template.combat_traits:
        return False
    if critical or DamageType.RADIANT in damage_types:
        return False
    if dice is None:
        raise ValueError("Undead Fortitude requires a dice provider for its Constitution saving throw.")
    bonus = state.template.saving_throw_bonuses.get("constitution")
    if bonus is None:
        raise ValueError(f"{state.template.name} lacks a Constitution saving throw bonus.")
    dc = 5 + damage_taken
    if dice.roll(20) + bonus < dc:
        return False
    state.current_hp = 1
    state.is_alive = True
    state.is_dead = False
    state.is_unconscious = False
    state.is_stable = False
    return True


def resolve_effect_bound_survival_save(state: CombatantState, dice: DiceProvider | None) -> bool:
    """Replace a non-instantly-lethal drop to zero before unconsciousness is applied."""
    try:
        rule = state.template.progression_features.effect_bound_survival_save
        if rule is None or rule.required_effect_id not in state.active_effect_ids:
            return False
        if dice is None:
            raise ValueError(f"{rule.source_id} requires a dice provider.")
        # Import at the resolution point: the shared save resolver also consumes Rage.
        from app.combat.saving_throw_rolls import resolve_saving_throw

        uses = state.survival_save_uses.get(rule.source_id, 0)
        dc = rule.initial_dc + uses * rule.dc_increment
        roll, succeeded = resolve_saving_throw(state, rule.save_ability, dc, dice)
        # A failed attempt still increases the next DC. Fight construction resets this map.
        state.survival_save_uses[rule.source_id] = uses + 1
        if succeeded:
            state.current_hp = rule.replacement_hp
            state.is_alive = True
            state.is_dead = False
            state.is_unconscious = False
            state.is_stable = False
        evidence = f"rolls {roll.rolls}, modifier {roll.modifier}, total {roll.total}" if roll else "automatic failure"
        state.pending_survival_save_logs.append(
            f"{state.template.name} {rule.source_id}: DC {dc} {rule.save_ability} save; "
            f"{evidence}; {'succeeds' if succeeded else 'fails'}; HP {state.current_hp}; "
            f"next DC {dc + rule.dc_increment}."
        )
        return succeeded
    except Exception:
        logger.exception("Effect-bound survival save failed for %s.", state.template.id)
        raise


def consume_survival_save_log(state: CombatantState) -> str:
    """Move already-resolved save evidence onto its damage event without rolling again."""
    try:
        result = " ".join(state.pending_survival_save_logs)
        state.pending_survival_save_logs.clear()
        return f" {result}" if result else ""
    except Exception:
        logger.exception("Survival save audit failed for %s.", state.template.id)
        raise
