"""Pin inert elemental innate options to complete 2014 printed-source proof.

Schema: the immutable source supplies the complete spell list, frequencies,
save DC, attack bonus, shared pool and qualifiers. There is no runtime
monster-name dispatch; returned IDs only suppress uncastable/communication-only
choices in the automated arena, retaining all spells on reference cards.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_innate_source_2014 import (
    innate_spellcasting_source_2014, innate_spells_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Exact paragraph and the complete nine-row source list are both required.
# The actor is extracted from the source, not used for identity dispatch.
_PRINTED = re.compile(
    r"The (?P<actor>[a-z][a-z' -]*)'s innate spellcasting ability is Charisma "
    r"\(spell save DC (?P<dc>\d+), \+(?P<bonus>\d+) to hit with spell attacks\)\. "
    r"It can innately cast the following spells, requiring no material components: "
    r"At will: detect magic "
    r"3/day: enlarge/reduce, tongues "
    r"1/day each: conjure elemental \(fire elemental only\), gaseous form, "
    r"invisibility, major image, plane shift, wall of fire",
    re.IGNORECASE,
)

_EXPECTED = (
    ("detect-magic", "detect magic", "at_will", None, False, None),
    ("enlarge-reduce", "enlarge/reduce", "per_day", 3, True, None),
    ("tongues", "tongues", "per_day", 3, True, None),
    ("conjure-elemental", "conjure elemental", "per_day", 1, False, "fire elemental only"),
    ("gaseous-form", "gaseous form", "per_day", 1, False, None),
    ("invisibility", "invisibility", "per_day", 1, False, None),
    ("major-image", "major image", "per_day", 1, False, None),
    ("plane-shift", "plane shift", "per_day", 1, False, None),
    ("wall-of-fire", "wall of fire", "per_day", 1, False, None),
)
_FIELDS = ("id", "name", "usage", "uses_per_day", "shared_pool", "qualifier")

# No creature is summoned into the Pit; Tongues only communicates; and a
# voluntary Gaseous Form loses the normal violence-first combat action.
# Major Image retains its complete printed illusion. The standard automated
# ring has no illusion-belief, decoy, or objective interaction for the AI to
# exploit, so the caster declines that non-damaging Action rather than gaining
# invented obscuration/debuff mechanics. This is AI exclusion, NOT a claim
# that Major Image lacks 2014 tabletop combat effects. Enlarge/Reduce is
# separately bound as an actual combat buff, never excluded.
_ARENA_AI_EXCLUDED = frozenset({
    "tongues", "conjure-elemental", "gaseous-form", "major-image",
})


def source_proven_elemental_inert_spells_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Approve only noncombat options in one fully proven source spell list."""
    try:
        source = innate_spellcasting_source_2014(monster)
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return frozenset()
        if source.get("unsupported_text") is not None:
            return frozenset()
        if (source.get("ability"), source.get("save_dc"), source.get("attack_bonus")) != (
            "charisma", 15, 7,
        ):
            return frozenset()
        section = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Innate Spellcasting", "")
        match = _PRINTED.fullmatch(" ".join(section.replace("’", "'").split()))
        if match is None or (int(match["dc"]), int(match["bonus"])) != (15, 7):
            return frozenset()
        rows = innate_spells_2014(monster)
        if len(rows) != len(_EXPECTED):
            return frozenset()
        if any(set(row) != set(_FIELDS) for row in rows):
            return frozenset()
        if tuple(tuple(row[key] for key in _FIELDS) for row in rows) != _EXPECTED:
            return frozenset()
        return _ARENA_AI_EXCLUDED
    except Exception:
        logger.exception("Failed 2014 elemental innate source proof for %s.", monster.id)
        raise
