"""Fight-local variable-head lifecycle shared by declarative card profiles."""
from __future__ import annotations
from app.domain.models import CombatantState


def initialize_variable_heads(state: CombatantState) -> None:
    profile = state.template.variable_heads
    state.current_heads = profile.initial_heads if profile else None
    state.heads_lost_since_owner_turn = 0
    state.head_regrowth_blocked = False
    refresh_opportunity_reactions(state)


def refresh_opportunity_reactions(state: CombatantState) -> None:
    profile = state.template.variable_heads
    state.opportunity_reactions_remaining = (
        max(0, int(state.current_heads or 0) - 1)
        if profile and profile.extra_opportunity_reactions_per_head_beyond_one else 0
    )


def opportunity_reaction_available(state: CombatantState) -> bool:
    return bool(state.reaction_available or state.opportunity_reactions_remaining > 0)


def spend_opportunity_reaction(state: CombatantState) -> None:
    if state.reaction_available:
        state.reaction_available = False
    elif state.opportunity_reactions_remaining > 0:
        state.opportunity_reactions_remaining -= 1
    else:
        raise ValueError("No Opportunity Attack reaction remains.")


def note_variable_head_damage(state: CombatantState, damage_before: dict[str, int]) -> bool:
    """Sever at most one head in the active creature's turn."""
    profile = state.template.variable_heads
    if profile is None or state.current_heads is None or state.current_heads <= 0:
        return False
    damage_after = state.damage_taken_this_turn_by_type
    if any(int(damage_after.get(kind, 0)) > int(damage_before.get(kind, 0))
           for kind in profile.regrowth_blocking_damage_types):
        state.head_regrowth_blocked = True
    before_total = sum(int(value) for value in damage_before.values())
    after_total = sum(int(value) for value in damage_after.values())
    if before_total < profile.sever_damage_threshold <= after_total:
        state.current_heads -= 1
        state.heads_lost_since_owner_turn += 1
        state.opportunity_reactions_remaining = min(
            state.opportunity_reactions_remaining, max(0, state.current_heads - 1),
        )
        return state.current_heads == 0
    return False


def end_owner_turn(state: CombatantState) -> tuple[int, int]:
    """Regrow and heal at the owner's turn end, then reset that window."""
    profile = state.template.variable_heads
    if profile is None:
        return 0, 0
    grown = healed = 0
    if (not state.is_dead and (state.current_heads or 0) > 0
            and state.heads_lost_since_owner_turn > 0 and not state.head_regrowth_blocked):
        grown = state.heads_lost_since_owner_turn * profile.heads_per_regrowth
        state.current_heads = int(state.current_heads or 0) + grown
        refresh_opportunity_reactions(state)
        from app.combat.zero_hp import restore_hit_points
        healed = restore_hit_points(state, grown * profile.healing_per_regrown_head)
    state.heads_lost_since_owner_turn = 0
    state.head_regrowth_blocked = False
    return grown, healed


def current_heads_save_advantage(state: CombatantState, condition_id: str | None) -> bool:
    """True when more than one head grants Advantage vs the listed conditions."""
    profile = state.template.variable_heads
    if not profile or not condition_id or (state.current_heads or 0) <= 1:
        return False
    return condition_id.casefold() in {c.casefold() for c in profile.save_advantage_conditions}
