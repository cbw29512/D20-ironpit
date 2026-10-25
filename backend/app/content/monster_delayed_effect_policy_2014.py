"""Arena policy for printed monster effects with hour-scale delays."""
from __future__ import annotations

ARENA_DELAY_CUTOFF_HOURS_2014 = 1


def delayed_effect_is_arena_neutral_2014(delay_hours: object) -> bool:
    """Return whether a required delay cannot affect an Iron Pit fight."""
    if isinstance(delay_hours, bool) or not isinstance(delay_hours, int):
        raise ValueError("2014 delayed-effect hours must be an integer.")
    if delay_hours < 0:
        raise ValueError("2014 delayed-effect hours cannot be negative.")
    return delay_hours > ARENA_DELAY_CUTOFF_HOURS_2014


def arena_active_delayed_max_hp_fields_2014(
    row: dict[str, object],
) -> dict[str, object]:
    """Compile delayed max-HP fields only when their delay can occur in-fight."""
    delay_hours = row.get("delayed_max_hp_reduction_delay_hours")
    if delayed_effect_is_arena_neutral_2014(delay_hours):
        return {}
    return {
        "delayed_max_hp_reduction_delay_hours": delay_hours,
        "delayed_max_hp_reduction_dice_count": int(
            row["delayed_max_hp_reduction_dice_count"]
        ),
        "delayed_max_hp_reduction_dice_size": int(
            row["delayed_max_hp_reduction_dice_size"]
        ),
        "delayed_max_hp_reduction_zero_kills": bool(
            row["delayed_max_hp_reduction_zero_kills"]
        ),
    }
