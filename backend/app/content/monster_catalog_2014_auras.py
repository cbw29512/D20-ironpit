from __future__ import annotations

import re

from app.domain.auras import StartTurnAura

_STENCH = re.compile(
    r"Stench\.\s*Any creature that starts its turn within (?P<range>\d+) feet of the [^.]+ "
    r"must succeed on a DC (?P<dc>\d+) Constitution saving throw or be poisoned until the start of its next turn\. "
    r"On a successful saving throw, the creature is immune to the [^.]+ stench for 24 hours\.",
    re.I,
)


def start_turn_auras_2014(source_traits: str | None) -> list[StartTurnAura]:
    if not source_traits or "Stench." not in source_traits:
        return []
    text = re.sub(r"<[^>]+>", "", source_traits)
    match = _STENCH.search(text)
    if match is None:
        raise ValueError("Stench source text is not a supported start-turn aura shape.")
    return [StartTurnAura(
        id="stench", name="Stench", range_ft=int(match.group("range")),
        save_ability="constitution", save_dc=int(match.group("dc")),
        failure_condition_id="poisoned", success_grants_source_immunity=True,
    )]
