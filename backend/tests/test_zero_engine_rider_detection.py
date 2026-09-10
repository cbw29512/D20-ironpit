from __future__ import annotations

from scripts.report_zero_engine_monsters import _unmodeled_action_rider


def test_max_hp_reduction_is_not_misclassified_as_zero_engine_safe() -> None:
    try:
        actions = (
            "Life Drain. Melee Attack Roll: +4, reach 5 ft. Hit: 7 (2d6) Necrotic damage. "
            "If the target is a creature, its Hit Point maximum decreases by an amount equal to the damage taken."
        )
        assert _unmodeled_action_rider(actions) is True
    except Exception:
        raise


def test_plain_attack_remains_zero_engine_rider_safe() -> None:
    try:
        actions = "Slam. Melee Attack Roll: +4, reach 5 ft. Hit: 7 (2d6) Bludgeoning damage."
        assert _unmodeled_action_rider(actions) is False
    except Exception:
        raise
