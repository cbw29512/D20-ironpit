"""Direct HP loss has no damage defenses, temp HP, or damage-trigger side effects."""

from types import SimpleNamespace

from app.combat.hit_point_loss import lose_hit_points
from app.combat.start_of_turn_hp_loss import resolve_start_of_turn_hp_loss_events
from app.combat.state import build_combatant_state
from app.combat.dice import FixedDiceProvider
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters_low_cr import build_giant_rat
from app.domain.encounters import EncounterCombatant
from app.domain.timed_effects import TimedEffect


def _fighter():
    state = build_combatant_state(build_karnok_stoneward())
    state.current_hp = min(16, state.template.max_hp)
    state.temporary_hp = 12
    for resource in state.resources:
        if resource.id == "relentless-endurance":
            resource.current_uses = 0
    return state


def test_direct_hp_loss_ignores_temp_hp_and_damage_flags() -> None:
    state = _fighter()
    state.damage_taken_this_turn_by_type = {"fire": 2}
    before = state.current_hp
    assert lose_hit_points(state, 4) == 4
    assert state.current_hp == before - 4
    assert state.temporary_hp == 12
    assert state.damage_taken_this_turn_by_type == {"fire": 2}
    assert state.death_save_failures == 0


def test_direct_hp_loss_uses_nondamage_zero_hp_path() -> None:
    state = _fighter()
    state.current_hp = 2
    assert lose_hit_points(state, 8) == 2
    assert state.current_hp == 0
    assert state.is_unconscious
    assert not state.is_dead
    assert state.temporary_hp == 12
    assert state.death_save_failures == 0
    assert lose_hit_points(state, 10) == 0


def test_direct_hp_loss_causes_monster_zero_hp_transition() -> None:
    state = build_combatant_state(build_giant_rat())
    state.current_hp = 3
    assert lose_hit_points(state, 9) == 3
    assert state.is_dead
    assert state.current_hp == 0


def test_recurring_hp_loss_emits_loss_not_damage() -> None:
    state = _fighter()
    state.timed_effects.append(TimedEffect(
        effect_id="persistent-wound", source_id="source-one",
        source_effect_id="Printed Wound",
        start_of_turn_hp_loss_dice_count=2,
        start_of_turn_hp_loss_dice_size=10,
        expires_at_start_of_source_turn=False,
    ))
    member = EncounterCombatant(combatant_id="target", side="heroes", position_ft=0, state=state)
    setup = SimpleNamespace(heroes=[member], monsters=[])
    before = state.current_hp
    events, sequence = resolve_start_of_turn_hp_loss_events(
        1, 2, member, setup, FixedDiceProvider([3, 4]),
    )
    assert sequence == 2
    assert len(events) == 1
    assert state.current_hp == before - 7
    assert events[0].hp_before == before
    assert events[0].hp_after == before - 7
    assert "not damage" in events[0].description
    assert state.temporary_hp == 12
    assert state.death_save_failures == 0
