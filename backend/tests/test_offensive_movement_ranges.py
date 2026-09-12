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
        automatic_spell_actions=[],
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


def _movement_context(monkeypatch, *, distance: int, profiles, plan):
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
    monkeypatch.setattr(offensive_movement_policy, "living_opponents", lambda *_: [target])
    monkeypatch.setattr(offensive_movement_policy, "combatant_distance", lambda *_: distance)
    monkeypatch.setattr(
        offensive_movement_policy,
        "ranked_offensive_range_profiles_for_target",
        lambda *_: profiles,
    )
    monkeypatch.setattr(offensive_movement_policy, "plan_movement_toward", plan)
    return attacker, setup


def test_long_range_legal_attack_moves_toward_preferred_range(monkeypatch) -> None:
    profile = OffensiveRangeProfile(1, "ranged", 320, 80)
    fixed_plan = SimpleNamespace(
        goal_reachable=True, path=[SimpleNamespace(x=1, y=0)],
        final_distance_ft=70, movement_cost_ft=30,
    )
    attacker, setup = _movement_context(
        monkeypatch, distance=100, profiles=[profile], plan=lambda *_: fixed_plan
    )
    intent = offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    )
    assert intent is not None
    assert intent.target_id == "target"
    assert intent.family == "ranged"
    assert intent.desired_distance_ft == 80


def test_melee_only_partial_advance_is_selected_when_nothing_is_actionable(monkeypatch) -> None:
    profile = OffensiveRangeProfile(1, "melee", 5, 5)
    fixed_plan = SimpleNamespace(
        goal_reachable=True, path=[SimpleNamespace(x=1, y=0)],
        final_distance_ft=30, movement_cost_ft=30,
    )
    attacker, setup = _movement_context(
        monkeypatch, distance=60, profiles=[profile], plan=lambda *_: fixed_plan
    )
    intent = offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    )
    assert intent is not None
    assert intent.family == "melee"
    assert intent.desired_distance_ft == 5


def test_partial_melee_does_not_override_already_legal_ranged_offense(monkeypatch) -> None:
    profiles = [
        OffensiveRangeProfile(1, "melee", 5, 5, execution_rank=2, expected_value=20),
        OffensiveRangeProfile(1, "ranged", 120, 60, execution_rank=4, expected_value=5),
    ]

    def _plan(*args):
        desired = args[4]
        if desired == 5:
            return SimpleNamespace(
                goal_reachable=True, path=[SimpleNamespace(x=1, y=0)],
                final_distance_ft=30, movement_cost_ft=30,
            )
        return SimpleNamespace(
            goal_reachable=True, path=[SimpleNamespace(x=1, y=0)],
            final_distance_ft=80, movement_cost_ft=30,
        )

    attacker, setup = _movement_context(
        monkeypatch, distance=100, profiles=profiles, plan=_plan
    )
    assert offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    ) is None


def test_blocked_improvement_preserves_already_legal_attack(monkeypatch) -> None:
    profile = OffensiveRangeProfile(1, "ranged", 320, 80)
    fixed_plan = SimpleNamespace(
        goal_reachable=False, path=[], final_distance_ft=100, movement_cost_ft=0,
    )
    attacker, setup = _movement_context(
        monkeypatch, distance=100, profiles=[profile], plan=lambda *_: fixed_plan
    )
    assert offensive_movement_policy.choose_offensive_movement_intent(
        attacker, setup, "round-1:attacker"
    ) is None


def test_range_profile_rejects_preferred_distance_beyond_legal_maximum() -> None:
    with pytest.raises(ValueError, match="Preferred offensive range"):
        OffensiveRangeProfile(1, "ranged", 80, 320)
