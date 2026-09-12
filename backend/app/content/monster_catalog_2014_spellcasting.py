from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014

ARENA_NEUTRAL_REGULAR_SPELLS = frozenset({
    "detect-magic",
    "identify",
    "light",
    "mage-hand",
    "prestidigitation",
    "scrying",
    "thaumaturgy",
    "water-breathing",
})


def unresolved_spellcasting_2014(source: CatalogMonster2014) -> list[str]:
    if "Spellcasting" not in source.trait_names:
        return []
    profile = source.spellcasting
    if profile is None or not profile.source_complete or not profile.spells:
        return ["unparsed-source"]
    return [
        spell.name
        for spell in profile.spells
        if spell.id not in ARENA_NEUTRAL_REGULAR_SPELLS
    ]
