from __future__ import annotations

from app.domain.models import CombatantState


def immunity_key(source_id: str, source_effect_id: str) -> str:
    return f"{source_id}::{source_effect_id}"


def source_effect_is_immune(
    state: CombatantState,
    source_id: str,
    source_effect_id: str,
) -> bool:
    return immunity_key(source_id, source_effect_id) in state.source_effect_immunities


def grant_source_effect_immunity(
    state: CombatantState,
    source_id: str,
    source_effect_id: str,
) -> str:
    key = immunity_key(source_id, source_effect_id)
    if key not in state.source_effect_immunities:
        state.source_effect_immunities.append(key)
    return key
