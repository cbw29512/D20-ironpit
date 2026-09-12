from types import SimpleNamespace

import pytest

from app.combat import offensive_movement_policy, offensive_ranges, offensive_weapon_ranges
from app.combat.offensive_range_profile import OffensiveRangeProfile
from app.domain.weapons import WeaponAttackKind


def _combatants_for_ranged_profile(normal_range: int = 80, long_range: int = 320):
    weapon = SimpleNamespace(
        attack_kind=WeaponAttackKind.RANGED,
        reach_ft=5,
        normal_range_ft=normal_range,
        long_range_ft=long_range,
    )
    attack = SimpleNamespace(id="ranged", weapon=weapon, resource_id=None, resource_cost=1)
    template = SimpleNamespace(
        weapon_attack=attack,
        alternate_weapon_attacks=[],
        attack_action=None,
        spell_attack_actions=[],
        spell_save_actions=[],
        saving_throw_actions=[],
    )
    attacker = SimpleNamespace(
        combatant_id="attacker", state=SimpleNamespace(template=template)
    )
    target = SimpleNamespace(
        combatant_id="target",
        state=SimpleNamespace(template=SimpleNamespace(size="medium")),
    )
    return attacker, target


def test_ranged_profile_separates_legal_and_preferred_range(monkeypatch) -> None:
    attacker, target = _combatants_for_ranged_profile()
    monkeypatch.setattr(offensive_weapon_ranges, "attack_allowed_against", lambda *_: True)
    monkeypatch.setattr(offensive_weapon_ranges, "resource_available", lambda *_: True)
    monkeypatch.setattr(offensive_weapon_ranges, "is_recharge_resource", lambda *_: False)

    profiles = offensive_ranges.ranked_offensive_range_profiles_for_target(
        attacker, target, "round-1:attacker"
    )

    assert profiles == [
        OffensiveRangeProfile(
            priority=1,
            family="ranged",
            max_range_ft=320,
            preferred_range_ft=80,
            execution_rank=4,
        )
    ]


def _movement_context(monkeypatch, *, distance: int, profile: OffensiveRangeProfile, plan):
    attacker = SimpleNamespace(
        combatant_id="attacker",
        state=SimpleNamespace(
            position=SimpleNamespace(x=0, y=0), movement_remaining_ft=30
        ),
    )
    target = SimpleNamespace(
        combatant_id="target",
        state=SimpleNamespace(position=SimpleNamespace(x=20, y=0)),
    )
    setup = SimpleNamespace(map_definition=object(), heroes=[attacker], monsters=[target])
    monkeypatch.setattr(offensive_movement_policy, "is_available", lambda *_: True)
    monkeypatch.setattr(
        offensive_movement_policy, "living_opponents", lambda *_: [target]
    )
    monkeypatch.setattr(
        offensive_movement_policy, "combatant_distance", lambda *_: distance
    )
    monkeypatch.setattr(
        offensive_movement_policy,
        "ranked_offensive_range_profiles_for_target",
        lambda *_: [profile],
    )
    monkeypatch.setattr(
        offensive_movement_policy, "plan_movement_toward", lambda *_: plan
    )
    return attacker, setup


def test_long_range_legal_attack_moves_toward_preferred_range(monkeypatch) -> None:
    profile = OffensiveRangeProfile(1, "ranged", 320, 80)
    plan = SimpleNamespace(
        goal_reachable=True,
        path=[SimpleNamespace(x=1, y=0)],
        final_distance_ft=70,
        movement_cost_ft=30,
    )
    attacker, setup = _movement_context(
        monkeypatch, distance=100, profile=profile, plan=plan
    )

    intent = offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    )

    assert intent is not None
    assert intent.target_id == "target"
    assert intent.family == "ranged"
    assert intent.desired_distance_ft == 80


def test_partial_advance_that_cannot_reach_preferred_range_is_not_selected(monkeypatch) -> None:
    profile = OffensiveRangeProfile(1, "melee", 5, 5)
    plan = SimpleNamespace(
        goal_reachable=True,
        path=[SimpleNamespace(x=1, y=0)],
        final_distance_ft=30,
        movement_cost_ft=30,
    )
    attacker, setup = _movement_context(
        monkeypatch, distance=60, profile=profile, plan=plan
    )

    assert offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    ) is None


def test_blocked_improvement_preserves_already_legal_attack(monkeypatch) -> None:
    profile = OffensiveRangeProfile(1, "ranged", 320, 80)
    plan = SimpleNamespace(
        goal_reachable=False,
        path=[],
        final_distance_ft=100,
        movement_cost_ft=0,
    )
    attacker, setup = _movement_context(
        monkeypatch, distance=100, profile=profile, plan=plan
    )

    intent = offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    )

    assert intent is None


def test_range_profile_rejects_preferred_distance_beyond_legal_maximum() -> None:
    with pytest.raises(ValueError, match="Preferred offensive range"):
        OffensiveRangeProfile(1, "ranged", 80, 320)
