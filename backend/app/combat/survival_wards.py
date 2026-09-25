from __future__ import annotations

import logging

from app.combat.timed_conditions import remove_effect_group
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def _source_name(effect) -> str:
    source = effect.source_effect_id or effect.effect_id
    return source.replace("-", " ").title()


def consume_survival_ward(
    state: CombatantState,
    *,
    nondamage_instant_death: bool = False,
) -> bool:
    """Consume the first active generic survival ward matching the incoming outcome."""
    try:
        candidates = [
            effect for effect in state.timed_effects
            if effect.zero_hp_replacement_hp > 0
            and (not nondamage_instant_death or effect.prevents_nondamage_instant_death)
        ]
        if not candidates:
            return False
        effect = candidates[0]
        remove_effect_group(state, effect)
        state.current_hp = effect.zero_hp_replacement_hp
        state.is_alive = True
        state.is_dead = False
        state.is_unconscious = False
        state.is_stable = False
        label = _source_name(effect)
        outcome = (
            "negates the instant-death effect"
            if nondamage_instant_death
            else f"keeps {state.template.name} at {effect.zero_hp_replacement_hp} HP"
        )
        state.pending_survival_save_logs.append(f" {label} {outcome}.")
        return True
    except Exception:
        logger.exception("Failed to resolve survival ward for %s.", state.template.name)
        raise
