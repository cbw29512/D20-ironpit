"""2014 source-owned proof of Duergar Resilience save advantages.

Exact printed clause only; no name dispatch. Immutable source remains unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

_DUERGAR_RESILIENCE = re.compile(
    r"The duergar has advantage on saving throws against poison, spells, and illusions, "
    r"as well as to resist being charmed or paralyzed\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SourceDuergarResilience2014:
    source_name: str = "Duergar Resilience"
    magical_effect_advantage: bool = True
    effect_tags: tuple[str, ...] = ("poison", "charmed", "paralyzed")


def source_duergar_resilience_2014(
    monster: SourceMonster2014,
) -> SourceDuergarResilience2014 | None:
    """Return only a fully verified 2014 Duergar Resilience source profile."""
    if "Duergar Resilience" not in monster.trait_names:
        return None
    text = source_sections_2014(
        monster.source_traits, include_continuations=True,
    ).get("Duergar Resilience")
    if text is None or _DUERGAR_RESILIENCE.fullmatch(text.strip()) is None:
        return None
    return SourceDuergarResilience2014()
