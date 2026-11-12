"""Fail-closed source proof for intrinsically noncombat innate weather/height magic.

State model: environmental utility spells remain immutable card metadata.
They do not acquire combat Actions, duration timers, or Recharge resources.
Only a complete printed source and matching parsed spell declarations qualify.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_source_2014 import innate_spellcasting_source_2014, innate_spells_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_innate_fog_cloud_2014 import source_proven_innate_fog_cloud_2014

logger = logging.getLogger(__name__)

_SOURCE_UTILITY_CLAUSE = (
    "The giant's innate spellcasting ability is Charisma (spell save DC 17). "
    "It can innately cast the following spells, requiring no material components: "
    "At will: detect magic, feather fall, levitate, light "
    "3/day each: control weather, water breathing"
)
_PRINTED_SPELLS = (
    ("detect-magic", "at_will", None),
    ("feather-fall", "at_will", None),
    ("levitate", "at_will", None),
    ("light", "at_will", None),
    ("control-weather", "per_day", 3),
    ("water-breathing", "per_day", 3),
)
# Detect Magic already has the standard source-neutral classification.
_ENVIRONMENT_ONLY_IDS = frozenset({
    "feather-fall", "levitate", "light", "control-weather", "water-breathing",
})


def source_proven_arena_inert_innate_spells_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Use printed text/metadata rather than monster identity to admit inert spells."""
    try:
        card = innate_spellcasting_source_2014(monster)
        if card is None or not card.get("source_complete"):
            return frozenset()
        # The shared Fog Cloud source proof validates the ENTIRE Cloud Giant
        # innate source paragraph and every parsed spell/use, independently
        # of monster identity. Light remains on the source card, but has no
        # arena Action or visibility effect under the locked Pit policy.
        if source_proven_innate_fog_cloud_2014(monster):
            printed_ids = {row.get("id") for row in innate_spells_2014(monster)}
            # Cloud Giant's complete source clause is validated by the Fog
            # Cloud proof. Feather Fall has no falling trigger in the flat Pit;
            # Control Weather cannot alter the Pit's fixed environment.
            if {"light", "feather-fall", "control-weather"} <= printed_ids:
                return frozenset({"light", "feather-fall", "control-weather"})
        if card.get("ability") != "charisma" or card.get("save_dc") != 17:
            return frozenset()
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Innate Spellcasting", "")
        if " ".join(printed.split()).casefold() != _SOURCE_UTILITY_CLAUSE.casefold():
            return frozenset()
        spell_rows = tuple(
            (spell.get("id"), spell.get("usage"), spell.get("uses_per_day"))
            for spell in innate_spells_2014(monster)
        )
        if spell_rows != _PRINTED_SPELLS:
            return frozenset()
        return _ENVIRONMENT_ONLY_IDS
    except Exception:
        logger.exception(
            "2014 noncombat innate source proof failed for %s", monster.id,
        )
        raise
