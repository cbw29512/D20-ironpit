"""Prove typed save damage scoring is independent of printed source names."""
from types import SimpleNamespace

from app.combat.printed_damage import save_mean_damage


def test_typed_save_action_expected_damage_uses_all_components() -> None:
    try:
        components = [
            SimpleNamespace(dice_count=3, dice_size=6, damage_bonus=4),
            SimpleNamespace(dice_count=3, dice_size=6, damage_bonus=4),
        ]
        for label in ("Synthetic Leap", "Renamed Homebrew"):
            action = SimpleNamespace(id=label, damage_components=components, damage_dice_count=0)
            assert save_mean_damage(action) == 29
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Typed save expected-damage regression failed")
        raise
