from __future__ import annotations

import app.combat.turbo as turbo
from app.combat.dice import SeededDiceProvider
from app.combat.turbo import run_seeded_encounter, run_turbo_batch
from app.domain.encounters import EncounterSelection
from app.domain.turbo import TurboBatchRequest


SELECTION = EncounterSelection(
    hero_ids=["karnok-stoneward-l1"],
    monster_ids=["srd-commoner"],
)


def _replay_payload(result) -> dict:
    payload = result.model_dump()
    payload.pop("battle_id", None)
    return payload


def test_seeded_dice_repeats_the_same_sequence() -> None:
    first = SeededDiceProvider(20260907)
    second = SeededDiceProvider(20260907)

    assert [first.roll(20) for _ in range(12)] == [second.roll(20) for _ in range(12)]


def test_seeded_encounter_replays_exact_events_and_state() -> None:
    first = run_seeded_encounter(SELECTION, 424242)
    replay = run_seeded_encounter(SELECTION, 424242)

    assert _replay_payload(first) == _replay_payload(replay)


def test_turbo_batch_is_reproducible_and_totals_only_valid_fights() -> None:
    request = TurboBatchRequest(selection=SELECTION, fights=5, batch_seed=123456)

    first = run_turbo_batch(request)
    second = run_turbo_batch(request)

    assert first == second
    assert first.requested_fights == 5
    assert first.valid_fights + first.engine_errors == 5
    assert first.heroes_wins + first.monsters_wins + first.draws == first.valid_fights
    assert len(first.fights) == first.valid_fights
    assert len({fight.seed for fight in first.fights}) == first.valid_fights


def test_turbo_excludes_engine_errors_and_continues(monkeypatch) -> None:
    original = turbo.run_seeded_encounter
    calls = 0

    def flaky_runner(selection, seed):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("synthetic engine rule error")
        return original(selection, seed)

    monkeypatch.setattr(turbo, "run_seeded_encounter", flaky_runner)
    result = run_turbo_batch(TurboBatchRequest(
        selection=SELECTION,
        fights=3,
        batch_seed=98765,
    ))

    assert result.requested_fights == 3
    assert result.valid_fights == 2
    assert result.engine_errors == 1
    assert result.heroes_wins + result.monsters_wins + result.draws == 2
    assert result.errors[0].fight_number == 2
    assert result.errors[0].message == "synthetic engine rule error"
