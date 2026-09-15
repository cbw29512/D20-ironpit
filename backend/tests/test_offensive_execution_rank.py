from types import SimpleNamespace

from app.combat import offensive_save_ranges, offensive_weapon_ranges
from app.domain.weapons import WeaponAttackKind


def _attack(attack_id: str):
    return SimpleNamespace(
        id=attack_id,
        resource_id=None,
        resource_cost=1,
        weapon=SimpleNamespace(
            attack_kind=WeaponAttackKind.MELEE,
            reach_ft=5,
            normal_range_ft=None,
            long_range_ft=None,
        ),
    )


def _save(action_id: str):
    return SimpleNamespace(
        id=action_id,
        action_cost="action",
        resource_id=None,
        resource_cost=1,
        area=None,
        range_ft=30,
    )


def test_profiles_match_resolver_stage_order(monkeypatch) -> None:
    multi_attack = _attack("multi-attack")
    standard_attack = _attack("standard-only")
    multi_save = _save("multi-save")
    ordinary_save = _save("ordinary-save")
    attack_action = SimpleNamespace(
        slots=[SimpleNamespace(
            attack_ids=["multi-attack"],
            save_action_ids=["multi-save"],
        )]
    )
    attacker = SimpleNamespace(
        combatant_id="attacker",
        state=SimpleNamespace(template=SimpleNamespace(
            attack_action=attack_action,
            weapon_attack=multi_attack,
            alternate_weapon_attacks=[standard_attack],
            saving_throw_actions=[multi_save, ordinary_save],
        )),
    )
    target = SimpleNamespace(state=SimpleNamespace())

    monkeypatch.setattr(offensive_weapon_ranges, "attack_allowed_against", lambda *_: True)
    monkeypatch.setattr(offensive_weapon_ranges, "resource_available", lambda *_: True)
    monkeypatch.setattr(offensive_weapon_ranges, "is_recharge_resource", lambda *_: False)
    monkeypatch.setattr(offensive_save_ranges, "is_available", lambda *_: True)
    monkeypatch.setattr(offensive_save_ranges, "save_action_target_eligible", lambda *_: True)
    monkeypatch.setattr(offensive_save_ranges, "resource_available", lambda *_: True)
    monkeypatch.setattr(offensive_save_ranges, "is_recharge_resource", lambda *_: False)
    monkeypatch.setattr(offensive_save_ranges, "save_action_expected_damage", lambda *_: 0.0)

    weapon_ranks = {
        profile.family + ":" + str(index): profile.execution_rank
        for index, profile in enumerate(offensive_weapon_ranges.weapon_profiles(attacker, target))
    }
    save_ranks = [
        profile.execution_rank
        for profile in offensive_save_ranges.save_action_profiles(attacker, target)
    ]

    assert list(weapon_ranks.values()) == [2, 4]
    assert save_ranks == [2, 3]
