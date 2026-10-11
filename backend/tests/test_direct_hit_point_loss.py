from app.combat.hit_point_loss import lose_hit_points
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters_low_cr import build_giant_rat


def test_raw_hp_loss_does_not_consume_temporary_hp_or_trigger_damage_defenses():
    state = build_combatant_state(build_karnok_stoneward())
    state.current_hp = 14
    state.temporary_hp = 25
    state.template.damage_immunities.append("necrotic")
    assert lose_hit_points(state, 6) == 6
    assert state.current_hp == 8
    assert state.temporary_hp == 25


def test_raw_hp_loss_at_zero_uses_canonical_life_transition():
    state = build_combatant_state(build_giant_rat())
    state.current_hp = 3
    state.temporary_hp = 50
    assert lose_hit_points(state, 10) == 3
    assert state.current_hp == 0 and state.is_dead
    assert state.temporary_hp == 50


def test_raw_hp_loss_keeps_ongoing_effect_until_its_own_removal():
    state = build_combatant_state(build_karnok_stoneward())
    state.current_hp = 20
    apply_timed_condition(
        state, "infernal-wound", "devil-one", source_effect_id="Glaive",
        start_of_turn_hp_loss_dice_count=2, start_of_turn_hp_loss_dice_size=10,
        expires_at_start_of_source_turn=False,
    )
    effect = state.timed_effects[0]
    assert effect.start_of_turn_hp_loss_dice_count == 2
    assert effect.start_of_turn_hp_loss_dice_size == 10
    assert lose_hit_points(state, 7) == 7
    assert effect in state.timed_effects
