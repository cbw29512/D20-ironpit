from __future__ import annotations

from app.combat.hit_points import effective_max_hp
from app.domain.models import BattleEvent, CombatantState, DamageType


def note_suppression(state: CombatantState, damage_types: set[DamageType]) -> None:
    profile = state.template.regeneration
    if profile is None or not damage_types:
        return
    if set(profile.suppressed_by_damage_types).intersection(damage_types):
        state.regeneration_suppressed = True


def holds_at_zero(state: CombatantState) -> bool:
    profile = state.template.regeneration
    return bool(profile and profile.survives_zero_until_turn)


def resolve_start_turn(
    sequence: int,
    round_number: int,
    actor_id: str,
    state: CombatantState,
) -> tuple[BattleEvent | None, bool]:
    """Resolve regeneration before ordinary turn-state initialization.

    Returns (event, died_at_start). Suppression is consumed by this start-of-turn check.
    """
    profile = state.template.regeneration
    if profile is None or state.is_dead:
        return None, False
    suppressed = state.regeneration_suppressed
    state.regeneration_suppressed = False
    hp_before = state.current_hp
    if suppressed or (profile.requires_positive_hp and hp_before <= 0):
        if hp_before <= 0 and profile.survives_zero_until_turn:
            state.is_alive = False; state.is_dead = True; state.is_unconscious = False; state.is_stable = False
            return BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=actor_id, actor_name=state.template.name, feature_id="regeneration",
                hp_before=0, hp_after=0, is_dead=True, animation="regeneration",
                description=f"{state.template.name}'s Regeneration is suppressed and it dies at the start of its turn.",
            ), True
        return None, False
    if hp_before <= 0 and not profile.survives_zero_until_turn:
        return None, False
    state.current_hp = min(effective_max_hp(state), hp_before + profile.amount)
    healed = state.current_hp - hp_before
    if healed <= 0:
        return None, False
    state.is_alive = True; state.is_dead = False; state.is_unconscious = False; state.is_stable = False
    state.death_save_successes = 0; state.death_save_failures = 0
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=actor_id, actor_name=state.template.name, feature_id="regeneration",
        hp_before=hp_before, hp_after=state.current_hp, is_dead=False, animation="regeneration",
        description=f"{state.template.name} regenerates {healed} hit point{'s' if healed != 1 else ''}.",
    ), False
