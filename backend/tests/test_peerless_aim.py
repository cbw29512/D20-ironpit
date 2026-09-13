from app.combat.peerless_aim import resolve_peerless_aim_miss
from app.combat.state import build_combatant_state, refresh_start_of_turn
from app.content.fighter_progression import build_karnok_stoneward_level


def test_fighter_level19_compiles_peerless_aim() -> None:
    template = build_karnok_stoneward_level(19)

    assert template.progression_features.peerless_aim is True


def test_peerless_aim_converts_one_miss_until_next_turn() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(19))

    hit, used = resolve_peerless_aim_miss(state, False)
    assert (hit, used) == (True, True)

    hit, used = resolve_peerless_aim_miss(state, False)
    assert (hit, used) == (False, False)

    refresh_start_of_turn(state)
    hit, used = resolve_peerless_aim_miss(state, False)
    assert (hit, used) == (True, True)


def test_peerless_aim_does_not_spend_on_an_existing_hit() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(19))

    assert resolve_peerless_aim_miss(state, True) == (True, False)
    assert resolve_peerless_aim_miss(state, False) == (True, True)
