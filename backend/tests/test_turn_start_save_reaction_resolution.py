from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.combat import turn_start_save_reactions as runtime
from app.domain.turn_start_save_reaction import TurnStartSaveReaction


def _encounter():
    rule = TurnStartSaveReaction(
        source_id="unnerving-mask", source_name="Unnerving Mask",
        range_ft=30, save_ability="wisdom", save_dc=14,
    )
    source_state = SimpleNamespace(
        template=SimpleNamespace(turn_start_save_reaction=rule, name="Reaction Source"),
        reaction_available=True,
    )
    target_state = SimpleNamespace(template=SimpleNamespace(name="Target"))
    source = SimpleNamespace(combatant_id="source", side="monsters", state=source_state)
    target = SimpleNamespace(combatant_id="target", side="heroes", state=target_state)
    setup = SimpleNamespace(heroes=[target], monsters=[source])
    return source, target, setup


@pytest.mark.parametrize("succeeded", [False, True])
def test_turn_start_resolution_spends_reaction_and_applies_only_on_failure(
    monkeypatch, succeeded,
) -> None:
    source, target, setup = _encounter()
    seen = []

    monkeypatch.setattr(runtime, "eligible_turn_start_reaction", lambda *_: True)

    def resolve(state, ability, dc, dice, context, **kwargs):
        seen.append(("save", ability, dc, context.condition_id))
        return None, succeeded

    def spend(state, cost):
        seen.append(("spend", cost))
        state.reaction_available = False

    def apply(state, effect, owner, **kwargs):
        seen.append(("condition", effect, owner, kwargs["expiry_timing"]))
        assert kwargs["expires_at_start_of_source_turn"] is False
        return effect

    monkeypatch.setattr(runtime, "resolve_saving_throw", resolve)
    monkeypatch.setattr(runtime, "spend", spend)
    monkeypatch.setattr(runtime, "apply_timed_condition", apply)

    events, sequence = runtime.resolve_turn_start_save_reactions(
        7, 1, target, setup, object(),
    )
    assert sequence == 8 and len(events) == 1
    assert events[0].feature_id == "unnerving-mask"
    assert events[0].save_dc == 14
    assert events[0].save_succeeded is succeeded
    assert ("save", "wisdom", 14, "frightened") in seen
    assert ("spend", "reaction") in seen
    assert source.state.reaction_available is False
    if succeeded:
        assert not any(item[0] == "condition" for item in seen)
        assert events[0].applied_condition_ids == []
    else:
        assert ("condition", "frightened", "source", "target_turn_end") in seen
        assert events[0].applied_condition_ids == ["frightened"]


def test_ineligible_turn_start_does_not_roll_or_spend(monkeypatch) -> None:
    source, target, setup = _encounter()
    monkeypatch.setattr(runtime, "eligible_turn_start_reaction", lambda *_: False)
    monkeypatch.setattr(runtime, "resolve_saving_throw",
                        lambda *_args, **_kwargs: pytest.fail("ineligible save"))
    events, sequence = runtime.resolve_turn_start_save_reactions(
        3, 2, target, setup, object(),
    )
    assert events == [] and sequence == 3
    assert source.state.reaction_available is True
