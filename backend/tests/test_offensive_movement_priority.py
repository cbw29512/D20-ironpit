from types import SimpleNamespace

from app.combat import offensive_movement_policy
from app.combat.offensive_range_profile import OffensiveRangeProfile


def test_movement_follows_resolver_family_order_before_cheapest_path(monkeypatch) -> None:
    attacker = SimpleNamespace(
        combatant_id="attacker",
        state=SimpleNamespace(
            position=SimpleNamespace(x=0, y=0),
            movement_remaining_ft=30,
        ),
    )
    target = SimpleNamespace(
        combatant_id="target",
        state=SimpleNamespace(position=SimpleNamespace(x=20, y=0)),
    )
    setup = SimpleNamespace(
        map_definition=object(),
        heroes=[attacker],
        monsters=[target],
    )
    profiles = [
        OffensiveRangeProfile(1, "ranged", 320, 80, execution_rank=2),
        OffensiveRangeProfile(1, "spell", 60, 60, execution_rank=1),
    ]

    monkeypatch.setattr(offensive_movement_policy, "is_available", lambda *_: True)
    monkeypatch.setattr(
        offensive_movement_policy, "living_opponents", lambda *_: [target]
    )
    monkeypatch.setattr(
        offensive_movement_policy, "combatant_distance", lambda *_: 120
    )
    monkeypatch.setattr(
        offensive_movement_policy,
        "ranked_offensive_range_profiles_for_target",
        lambda *_: profiles,
    )

    def _plan(*args):
        desired_distance = args[4]
        movement_cost = 5 if desired_distance == 80 else 30
        return SimpleNamespace(
            goal_reachable=True,
            path=[SimpleNamespace(x=1, y=0)],
            final_distance_ft=90,
            movement_cost_ft=movement_cost,
        )

    monkeypatch.setattr(offensive_movement_policy, "plan_movement_toward", _plan)

    intent = offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    )

    assert intent is not None
    assert intent.family == "spell"
    assert intent.desired_distance_ft == 60
