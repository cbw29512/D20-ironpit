from __future__ import annotations

from app.domain.runtime import CombatantState


def refresh_spell_turn_state(state: CombatantState, round_number: int) -> None:
    """Snapshot persistent/concentration legality once at the start of this creature's turn."""
    state.active_persistent_spell_expiry_rounds = {
        spell_id: expires_round
        for spell_id, expires_round in state.active_persistent_spell_expiry_rounds.items()
        if round_number < expires_round
    }
    state.spell_turn_active_ids = sorted(state.active_persistent_spell_expiry_rounds)
    state.spell_turn_concentration_locked = state.concentration is not None


def persistent_spell_active(state: CombatantState, spell_id: str) -> bool:
    return spell_id in state.spell_turn_active_ids


def initial_spell_cast_allowed(state: CombatantState, spell_id: str, *, concentration: bool = False) -> bool:
    if persistent_spell_active(state, spell_id):
        return False
    if concentration and state.spell_turn_concentration_locked:
        return False
    return True


def activate_persistent_spell(
    state: CombatantState,
    spell_id: str,
    round_number: int,
    duration_rounds: int,
) -> None:
    if duration_rounds < 1:
        raise ValueError("Persistent spell duration must be at least one round.")
    state.active_persistent_spell_expiry_rounds[spell_id] = round_number + duration_rounds
    if spell_id not in state.spell_turn_active_ids:
        state.spell_turn_active_ids.append(spell_id)
        state.spell_turn_active_ids.sort()


def lock_concentration_for_turn(state: CombatantState) -> None:
    state.spell_turn_concentration_locked = True
