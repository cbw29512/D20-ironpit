"""Source-neutral expiry of self-owned timed effects on a combat action."""
from __future__ import annotations

import logging
from typing import Literal

from app.combat.concentration import end_concentration
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)

OwnerEvent = Literal["attack", "spell_cast"]


def expire_on_owner_event(
    state: CombatantState, event: OwnerEvent,
    affected_states: list[CombatantState] | None = None,
) -> list[str]:
    """End only effects whose source card declares this exact event trigger."""
    try:
        if event not in ("attack", "spell_cast"):
            raise ValueError(f"Unknown owner effect-expiry event: {event}.")
        flag = "ends_on_owner_attack" if event == "attack" else "ends_on_owner_spell_cast"
        removed: list[str] = []
        for effect in list(state.timed_effects):
            if effect not in state.timed_effects or not getattr(effect, flag):
                continue
            source = state.concentration
            if source and source.effect_id == effect.source_effect_id and source.source_id == effect.source_id:
                ids = [
                    item.effect_id for item in state.timed_effects
                    if item.source_id == source.source_id
                    and item.source_effect_id == source.effect_id
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
    except Exception:
        logger.exception("Owner action effect expiry failed for %s (%s).", state.template.id, event)
        raise
