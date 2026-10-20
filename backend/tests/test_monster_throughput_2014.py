from __future__ import annotations

import pytest

from scripts.measure_monster_throughput_2014 import measure


def snapshot(blocked: int, entries: list[tuple[str, list[str]]]) -> dict:
    return {"monster_2014": {
        "blocked_monster_count": blocked,
        "unresolved_printed_abilities": [
            {"printed_name": name, "monsters": owners}
            for name, owners in entries
        ],
    }}


def test_measures_completed_source_ability_obligations_and_admissions_per_hour() -> None:
    before = snapshot(114, [("Gaze", ["Basilisk", "Medusa"]), ("Cloud", ["Dretch"])])
    after = snapshot(112, [("Cloud", ["Dretch"])])
    result = measure(before, after, 2)
    assert result["resolved_printed_ability_obligations"] == 2
    assert result["newly_source_admitted_monsters"] == 2
    assert result["net_abilities_per_hour"] == 1
    assert result["net_monsters_per_hour"] == 1
    assert result["resolved"] == [
        {"monster": "Basilisk", "ability": "Gaze"},
        {"monster": "Medusa", "ability": "Gaze"},
    ]


def test_regressions_reduce_net_throughput() -> None:
    result = measure(
        snapshot(114, [("Cloud", ["Dretch"])]),
        snapshot(115, [("Gaze", ["Basilisk"])]),
        1,
    )
    assert result["new_unresolved_ability_obligations"] == 1
    assert result["net_ability_obligations_resolved"] == 0
    assert result["net_monsters_per_hour"] == -1


def test_rejects_zero_or_negative_elapsed_hours() -> None:
    with pytest.raises(ValueError):
        measure(snapshot(1, []), snapshot(1, []), 0)


@pytest.mark.parametrize("invalid_hours", [float("nan"), float("inf"), float("-inf"), -2.0])
def test_rejects_nonfinite_or_negative_work_hours(invalid_hours: float) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        measure(snapshot(1, []), snapshot(1, []), invalid_hours)


def test_newly_admitted_monsters_never_reports_negative_count() -> None:
    result = measure(snapshot(1, []), snapshot(2, [("New blocker", ["Beast"])]), 2)
    assert result["newly_source_admitted_monsters"] == 0
    assert result["net_monsters_per_hour"] == -0.5
