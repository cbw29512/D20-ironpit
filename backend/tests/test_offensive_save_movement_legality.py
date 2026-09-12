from types import SimpleNamespace

from app.combat import offensive_save_ranges
from app.combat.save_action_legality import save_action_target_eligible
from app.domain.actions import SavingThrowAction


def _grapple_save() -> SavingThrowAction:
    return SavingThrowAction(
        id="grapple-save",
        name="Grapple Save",
        save_ability="strength",
        dc=13,
        range_ft=5,
        required_target_grappled_by_self=True,
    )


def _pair(*, grappled_by: str | None = None):
    action = _grapple_save()
    attacker = SimpleNamespace(
        combatant_id="attacker",
        state=SimpleNamespace(
            template=SimpleNamespace(saving_throw_actions=[action], attack_action=None),
        ),
    )
    sources = [] if grappled_by is None else [SimpleNamespace(source_id=grappled_by)]
    target = SimpleNamespace(
        combatant_id="target",
        state=SimpleNamespace(
            template=SimpleNamespace(size="medium"),
            grapple_sources=sources,
            timed_effects=[],
        ),
    )
    return attacker, target, action


def _patch_profile_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(offensive_save_ranges, "is_available", lambda *_: True)
    monkeypatch.setattr(offensive_save_ranges, "resource_available", lambda *_: True)
    monkeypatch.setattr(offensive_save_ranges, "is_recharge_resource", lambda *_: False)
    monkeypatch.setattr(offensive_save_ranges, "save_action_expected_damage", lambda *_: 0.0)


def test_save_target_eligibility_requires_actor_owned_grapple() -> None:
    attacker, target, action = _pair(grappled_by="other")

    assert save_action_target_eligible(action, target, attacker) is False


def test_movement_does_not_chase_ineligible_save_target(monkeypatch) -> None:
    attacker, target, _ = _pair(grappled_by="other")
    _patch_profile_dependencies(monkeypatch)

    assert offensive_save_ranges.save_action_profiles(attacker, target) == []


def test_movement_profiles_eligible_actor_owned_grapple_save(monkeypatch) -> None:
    attacker, target, _ = _pair(grappled_by="attacker")
    _patch_profile_dependencies(monkeypatch)

    profiles = offensive_save_ranges.save_action_profiles(attacker, target)

    assert len(profiles) == 1
    assert profiles[0].family == "ability"
    assert profiles[0].max_range_ft == 5


def test_movement_ignores_non_action_save_abilities(monkeypatch) -> None:
    attacker, target, action = _pair(grappled_by="attacker")
    attacker.state.template.saving_throw_actions = [
        action.model_copy(update={"action_cost": "reaction"})
    ]
    _patch_profile_dependencies(monkeypatch)

    assert offensive_save_ranges.save_action_profiles(attacker, target) == []
