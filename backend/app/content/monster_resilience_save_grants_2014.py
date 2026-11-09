"""Source-proven 2014 resilience composed from generic save-Advantage grants.

No combat resolver lives here. The pinned printed trait only supplies eligibility
parameters; Python and browser use the same generic save modifier machinery.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.progression import SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)

_TRAIT = "Duergar Resilience"
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
_PRINTED_CLAUSE = (
    "The duergar has advantage on saving throws against poison, spells, and "
    "illusions, as well as to resist being charmed or paralyzed."
)
# A spell qualifies independently of its magic type or condition. Other
# qualifying non-spell effects must declare their actual semantic effect tag.
_EFFECT_TAGS = ("poison", "illusion", "charm", "paralyzed")


def source_proven_resilience_grants_2014(
    monster: SourceMonster2014,
) -> list[SavingThrowAdvantageGrant]:
    """Compile a printed passive into existing per-context save Advantage."""
    try:
        if _TRAIT not in monster.trait_names:
            return []
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get(_TRAIT, "")
        normalize = lambda value: " ".join(value.casefold().replace("’", "'").split())
        # Reject changed source clauses instead of silently broadening defense.
        if normalize(printed) != normalize(_PRINTED_CLAUSE):
            return []
        grants = [
            SavingThrowAdvantageGrant(
                source_id="duergar-resilience-spells",
                source_name=_TRAIT,
                abilities=list(_ABILITIES),
                requires_spell_effect=True,
            ),
        ]
        grants.extend(
            SavingThrowAdvantageGrant(
                source_id=f"duergar-resilience-{tag}",
                source_name=_TRAIT,
                abilities=list(_ABILITIES),
                required_effect_tags=[tag],
            )
            for tag in _EFFECT_TAGS
        )
        return grants
    except Exception:
        logger.exception(
            "Failed to bind source-proven resilience for %s.", monster.name,
        )
        raise
