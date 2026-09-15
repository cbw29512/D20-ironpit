from types import SimpleNamespace

from app.combat import offensive_movement_policy
from app.combat.offensive_range_profile import OffensiveRangeProfile


def test_higher_value_option_beats_cheaper_movement_within_same_tier(monkeypatch) -> None:
    attacker = SimpleNamespace(
        combatant_id="attacker",
        state=SimpleNamespace(position=SimpleNamespace(x=0, y=0), movement_remaining_ft=30),
    )
    target = SimpleNamespace(
        combatant_id="target",
        state=SimpleNamespace(position=SimpleNamespace(x=20, y=0)),
    )
    setup = SimpleNamespace(map_definition=object(), heroes=[attacker], monsters=[target])
    profiles = [
        OffensiveRangeProfile(1, "spell", 90, 90, execution_rank=1, expected_value=4.0),
        OffensiveRangeProfile(1, "spell", 60, 60, execution_rank=1, expected_value=12.0),
    ]

    monkeypatch.setattr(offensive_movement_policy, "is_available", lambda *_: True)
    monkeypatch.setattr(offensive_movement_policy, "living_opponents", lambda *_: [target])
    monkeypatch.setattr(offensive_movement_policy, "combatant_distance", lambda *_: 120)
    monkeypatch.setattr(
        offensive_movement_policy,
        "ranked_offensive_range_profiles_for_target",
        lambda *_: profiles,
    )

    def _plan(*args):
        desired_distance = args[4]
        cost = 10 if desired_distance == 90 else 30
        return SimpleNamespace(
            goal_reachable=True,
            path=[SimpleNamespace(x=1, y=0)],
            final_distance_ft=desired_distance,
            movement_cost_ft=cost,
        )

    monkeypatch.setattr(offensive_movement_policy, "plan_movement_toward", _plan)

    intent = offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "1:attacker"
    )

    assert intent is not None
    assert intent.family == "spell"
    assert intent.desired_distance_ft == 60
