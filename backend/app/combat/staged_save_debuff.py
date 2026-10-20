"""Universal save-driven debuff progression independent of source or trigger."""
from __future__ import annotations


def resolve_staged_save(*, save_total: int, dc: int, initial_effect: str,
                        terminal_effect: str, previous_effect: str | None = None,
                        immediate_failure_margin: int | None = None) -> str | None:
    """Return the next debuff, or None when the save clears it.

    Cards own DC, effect IDs, and failure thresholds. Trigger and visibility
    gating occur upstream; no monster, class, or spell identity is inspected.
    """
    if (type(save_total) is not int or type(dc) is not int or dc < 1
            or type(initial_effect) is not str or not initial_effect.strip()
            or type(terminal_effect) is not str or not terminal_effect.strip()
            or initial_effect == terminal_effect
            or previous_effect not in (None, initial_effect)
            or (immediate_failure_margin is not None and
                (type(immediate_failure_margin) is not int or immediate_failure_margin < 1))):
        raise ValueError("Invalid staged saving throw configuration")
    if save_total >= dc:
        return None
    if previous_effect == initial_effect or (
        immediate_failure_margin is not None and dc - save_total >= immediate_failure_margin
    ):
        return terminal_effect
    return initial_effect
