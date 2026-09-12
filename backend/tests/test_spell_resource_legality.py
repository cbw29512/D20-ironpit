from types import SimpleNamespace

from app.combat import offensive_ranges
from app.combat.spellcasting import spell_action_resource_available


def _state(*, resources, spent_turn: str | None = None):
    return SimpleNamespace(
        template=SimpleNamespace(id="caster", name="Caster"),
        resources=resources,
        spell_slot_expended_turn_key=spent_turn,
    )


def _resource(resource_id: str, uses: int):
    return SimpleNamespace(id=resource_id, current_uses=uses)


def test_standard_slot_spell_obeys_one_slot_per_turn_gate() -> None:
    state = _state(
        resources=[_resource("spell-slot-1", 1)],
        spent_turn="1:caster",
    )

    assert spell_action_resource_available(
        state,
        level=1,
        resource_id=None,
        resource_cost=1,
        turn_key="1:caster",
    ) is False


def test_explicit_non_slot_spell_resource_ignores_slot_turn_gate() -> None:
    state = _state(
        resources=[_resource("arcane-charge", 1)],
        spent_turn="1:caster",
    )

    assert spell_action_resource_available(
        state,
        level=1,
        resource_id="arcane-charge",
        resource_cost=1,
        turn_key="1:caster",
    ) is True


def test_explicit_spell_resource_must_have_required_uses() -> None:
    state = _state(resources=[_resource("arcane-charge", 0)])

    assert spell_action_resource_available(
        state,
        level=1,
        resource_id="arcane-charge",
        resource_cost=1,
        turn_key="1:caster",
    ) is False


def test_movement_inventories_automatic_spell_with_custom_resource(monkeypatch) -> None:
    action = SimpleNamespace(
        id="automatic-bolt",
        action_cost="action",
        level=1,
        resource_id="arcane-charge",
        resource_cost=1,
        range_ft=60,
    )
    template = SimpleNamespace(
        id="caster",
        name="Caster",
        spell_attack_actions=[],
        spell_save_actions=[],
        automatic_spell_actions=[action],
    )
    attacker = SimpleNamespace(
        combatant_id="caster",
        state=SimpleNamespace(
            template=template,
            resources=[_resource("arcane-charge", 1)],
            spell_slot_expended_turn_key="1:caster",
        ),
    )
    monkeypatch.setattr(offensive_ranges, "is_available", lambda *_: True)

    profiles = offensive_ranges._spell_profiles(attacker, "1:caster")

    assert len(profiles) == 1
    assert profiles[0].family == "spell"
    assert profiles[0].max_range_ft == 60
