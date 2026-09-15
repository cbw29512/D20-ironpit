from types import SimpleNamespace

from app.combat import attack_action_choices


def test_multiattack_save_choice_passes_actor_to_legality(monkeypatch) -> None:
    action = SimpleNamespace(id="actor-owned-save", resource_id=None, resource_cost=1, range_ft=5)
    attacker = SimpleNamespace(
        combatant_id="attacker",
        state=SimpleNamespace(template=SimpleNamespace(saving_throw_actions=[action])),
    )
    target = SimpleNamespace(combatant_id="target")
    setup = SimpleNamespace()
    slot = SimpleNamespace(save_action_ids=[action.id])

    monkeypatch.setattr(attack_action_choices, "target_order", lambda *_: [target])
    monkeypatch.setattr(attack_action_choices, "resource_available", lambda *_: True)
    monkeypatch.setattr(attack_action_choices, "save_distance", lambda *_: 5)
    monkeypatch.setattr(
        attack_action_choices,
        "legal_save_action",
        lambda candidate, chosen_target, distance, actor: (
            candidate is action and chosen_target is target and distance == 5 and actor is attacker
        ),
    )

    choice = attack_action_choices.save_choice(attacker, setup, slot)

    assert choice == (target, action, 5)
