from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014

# These spells cannot change a standard Iron Pit combat outcome by themselves.
ARENA_NEUTRAL_SPELLS = frozenset({
    "commune", "control-weather", "create-food-and-water", "creation",
    "dancing-lights", "detect-evil-and-good", "detect-magic", "disguise-self",
    "dream", "druidcraft", "identify", "light", "mage-hand", "nondetection",
    "prestidigitation", "raise-dead", "resurrection", "scrying", "thaumaturgy",
    "tongues", "water-breathing",
})


def unresolved_spells_2014(source: CatalogMonster2014) -> list[str]:
    """Return unsupported combat spells independent of casting origin.

    Prepared/slot casting and innate casting share the same universal spell resolver.
    Their source distinction only controls resource semantics: slots vs at-will/X-per-day.
    """
    unresolved: list[str] = []
    if "Spellcasting" in source.trait_names:
        profile = source.spellcasting
        if profile is None or not profile.source_complete or not profile.spells:
            unresolved.append("unparsed-regular-spellcasting")
        else:
            unresolved.extend(spell.name for spell in profile.spells if spell.id not in ARENA_NEUTRAL_SPELLS)
    if "Innate Spellcasting" in source.trait_names:
        profile = source.innate_spellcasting
        if profile is None or not profile.source_complete or not profile.spells:
            unresolved.append("unparsed-innate-spellcasting")
        else:
            unresolved.extend(spell.name for spell in profile.spells if spell.id not in ARENA_NEUTRAL_SPELLS)
    return list(dict.fromkeys(unresolved))
