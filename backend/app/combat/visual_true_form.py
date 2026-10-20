"""Observe the true form behind a source-neutral magical visual disguise."""
from __future__ import annotations

from app.combat.effective_senses import effective_sense_range_ft
from app.domain.runtime import CombatantState


def observer_sees_true_form(
    source: CombatantState, observer: CombatantState, distance_ft: int,
) -> bool:
    """Do not confuse recognizing an illusion with seeing the real form.

    Truesight sees through *magical* visual disguises inside its live range,
    including suppression rules. A separately concealed true form remains
    concealed; seeing through a magical illusion doesn't reveal physical cover.
    """
    if type(distance_ft) is not int or distance_ft < 0:
        raise ValueError("True-form visibility requires a valid nonnegative distance.")
    if type(source.true_form_visible) is not bool or type(source.magical_visual_disguise_active) is not bool:
        raise ValueError("Invalid fight-local true-form visibility state.")
    if not source.true_form_visible:
        return False
    if not source.magical_visual_disguise_active:
        return True
    truesight_ft = effective_sense_range_ft(observer, "truesight")
    return truesight_ft > 0 and distance_ft <= truesight_ft
