from __future__ import annotations

import re

from app.domain.gaze import StartTurnGaze

_RANGE = re.compile(r"within (\d+) feet", re.I)
_DC = re.compile(r"DC (\d+) Constitution saving throw", re.I)
_MARGIN = re.compile(r"fails the saving throw by (\d+) or more", re.I)


def petrifying_gaze_2014(source_traits: str | None) -> StartTurnGaze | None:
    if not source_traits or "Petrifying Gaze" not in source_traits:
        return None
    text = source_traits[source_traits.index("Petrifying Gaze"):]
    range_match = _RANGE.search(text); dc_match = _DC.search(text)
    required = ("restrained" in text.lower() and "petrified" in text.lower()
                and "end of its next turn" in text.lower() and "avert its eyes" in text.lower())
    if range_match is None or dc_match is None or not required:
        raise ValueError("Petrifying Gaze source text is not a supported staged-gaze shape.")
    margin_match = _MARGIN.search(text)
    margin = int(margin_match.group(1)) if margin_match else None
    return StartTurnGaze(
        id="petrifying-gaze", name="Petrifying Gaze", range_ft=int(range_match.group(1)),
        save_ability="constitution", save_dc=int(dc_match.group(1)),
        failure_condition_id="restrained", repeat_save_failure_condition_id="petrified",
        immediate_failure_margin=margin,
        immediate_failure_condition_id="petrified" if margin is not None else None,
    )
