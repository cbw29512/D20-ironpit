from types import SimpleNamespace

from app.combat import attack_actions
from app.domain.models import WeaponAttackKind


def test_multiattack_settles_lethal_event_before_next_slot(monkeypatch) -> None:
    """A death trigger from slot one can end the attacker before slot two begins."""
    definition = SimpleNamespace(
        id="test-multiattack",
        is_attack_action=False,
        slots=[SimpleNamespace(attack_ids=["test"]), SimpleNamespace(attack_ids=["test"])],
    )
    attacker_state = SimpleNamespace(
        template=SimpleNamespace(attack_action=definition),
        is_dead=False,
        is_unconscious=False,
        turn_terminated=False,
    )
    attacker = SimpleNamespace(combatant_id="attacker", state=attacker_state)
    target = SimpleNamespace(combatant_id="target", state=SimpleNamespace())
    setup = SimpleNamespace(heroes=[attacker], monsters=[target])
    weapon = SimpleNamespace(attack_kind=WeaponAttackKind.MELEE, light=False)
    attack = SimpleNamespace(weapon=weapon)
    calls = {"attacks": 0, "death": 0}

    monkeypatch.setattr(attack_actions, "validate_attack_action_slots", lambda _attacker: None)
    monkeypatch.setattr(attack_actions, "is_available", lambda _state, _cost: True)
    monkeypatch.setattr(attack_actions, "spend", lambda _state, _cost: None)
    monkeypatch.setattr(attack_actions, "slot_has_legal_choice", lambda *_args: True)
    monkeypatch.setattr(attack_actions, "opening_feature_id", lambda *_args: None)
    monkeypatch.setattr(attack_actions, "use_ranged_split", lambda *_args: False)
    monkeypatch.setattr(attack_actions, "forced_movement_choice", lambda *_args: None)
    monkeypatch.setattr(attack_actions, "attack_choice", lambda *_args, **_kwargs: (target, attack, 5))
    monkeypatch.setattr(attack_actions, "save_choice", lambda *_args: None)
    monkeypatch.setattr(attack_actions, "pack_tactics_active", lambda *_args: False)
    monkeypatch.setattr(attack_actions, "close_ranged_threat_exists", lambda *_args: False)

    def resolve_attack(sequence, *_args, **_kwargs):
        calls["attacks"] += 1
        return SimpleNamespace(sequence=sequence, event_type="attack", target_id="target", is_dead=True)

    def settle_death(sequence, *_args, **_kwargs):
        calls["death"] += 1
        attacker_state.is_dead = True
        return [SimpleNamespace(sequence=sequence, event_type="saving_throw")], sequence + 1

    monkeypatch.setattr(attack_actions, "resolve_encounter_attack", resolve_attack)
    monkeypatch.setattr(attack_actions, "resolve_event_death_triggers", settle_death)
    monkeypatch.setattr(
        attack_actions,
        "resolve_cleave_extra_attack",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("cleave ran after attacker died")),
    )

    events, sequence = attack_actions.resolve_attack_action(1, 1, attacker, setup, SimpleNamespace())

    assert [event.event_type for event in events] == ["attack", "saving_throw"]
    assert calls == {"attacks": 1, "death": 1}
    assert sequence == 3
    assert attacker_state.is_dead is True
