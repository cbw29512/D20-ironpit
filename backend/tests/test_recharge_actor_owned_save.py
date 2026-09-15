from types import SimpleNamespace

from app.combat import recharge_action_policy


def test_recharge_save_choice_passes_actor_to_legality(monkeypatch) -> None:
    action = SimpleNamespace(
        id="recharge-save",
        area=None,
        resource_id="recharge",
        resource_cost=1,
        range_ft=5,
    )
    attacker = SimpleNamespace(
        combatant_id="attacker",
        state=SimpleNamespace(template=SimpleNamespace(saving_throw_actions=[action])),
    )
    target = SimpleNamespace(combatant_id="target")
    setup = SimpleNamespace()

    monkeypatch.setattr(recharge_action_policy, "target_order", lambda *_: [target])
    monkeypatch.setattr(recharge_action_policy, "is_recharge_resource", lambda *_: True)
    monkeypatch.setattr(recharge_action_policy, "resource_available", lambda *_: True)
    monkeypatch.setattr(recharge_action_policy, "save_distance", lambda *_: 5)
    monkeypatch.setattr(
        recharge_action_policy,
        "legal_save_action",
        lambda candidate, chosen_target, distance, actor: (
            candidate is action and chosen_target is target and distance == 5 and actor is attacker
        ),
    )

    choice = recharge_action_policy.recharge_save_choice(attacker, setup)

    assert choice == (target, action, 5)
