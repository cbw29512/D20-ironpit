"""Source-neutral expiry of self-owned timed effects on owner combat events."""
from __future__ import annotations

import logging
from typing import Literal

from app.combat.concentration import end_concentration
from app.combat.timed_conditions import remove_effect_group
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)
OwnerEvent = Literal["attack", "spell_cast"]


def expire_on_owner_event(
    state: CombatantState,
    event: OwnerEvent,
    affected_states: list[CombatantState] | None = None,
) -> list[str]:
    try:
        if event not in ("attack", "spell_cast"):
            raise ValueError(f"Unknown owner effect-expiry event: {event}.")
        flag = "ends_on_owner_attack" if event == "attack" else "ends_on_owner_spell_cast"
        removed: list[str] = []
        for effect in list(state.timed_effects):
            if effect not in state.timed_effects or not getattr(effect, flag):
                continue
            concentration = state.concentration
            if (
                concentration is not None
                and concentration.effect_id == effect.source_effect_id
                and concentration.source_id == effect.source_id
            ):
                ids = [
                    item.effect_id
                    for item in state.timed_effects
                    if item.source_id == concentration.source_id
                    and item.source_effect_id == concentration.effect_id
                ]
                end_concentration(state, affected_states)
            else:
                ids = remove_effect_group(state, effect)
            for effect_id in ids:
                if effect_id not in removed:
                    removed.append(effect_id)
        return removed
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Owner-event expiry failed for %s (%s).", state.template.id, event)
        raise RuntimeError("Owner-event expiry could not be resolved.") from exc
