from __future__ import annotations

import re

from app.domain.save_auras import SaveAdvantageAura

_TURNING_DEFIANCE = re.compile(
    r"Turning Defiance\.\s*The [^.]+ and any ghouls within (?P<range>\d+) feet of it have advantage "
    r"on saving throws against effects that turn undead\.",
    re.I,
)


def save_advantage_auras_2014(source_traits: str | None) -> list[SaveAdvantageAura]:
    if not source_traits or "Turning Defiance." not in source_traits:
        return []
    text = re.sub(r"<[^>]+>", "", source_traits)
    match = _TURNING_DEFIANCE.search(text)
    if match is None:
        raise ValueError("Turning Defiance source text is not a supported save-advantage aura shape.")
    return [SaveAdvantageAura(
        id="turning-defiance", effect_id="turn-undead", range_ft=int(match.group("range")),
        includes_source=True, beneficiary_archetypes=["Ghoul"],
    )]
