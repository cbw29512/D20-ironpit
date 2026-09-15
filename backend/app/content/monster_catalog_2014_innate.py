from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014

ARENA_NEUTRAL_INNATE_SPELLS = frozenset({
    "commune",
    "control-weather",
    "create-food-and-water",
    "creation",
    "dancing-lights",
    "detect-evil-and-good",
    "detect-magic",
    "disguise-self",
    "dream",
    "druidcraft",
    "light",
    "mage-hand",
    "nondetection",
    "raise-dead",
    "resurrection",
    "scrying",
    "tongues",
    "water-breathing",
})


def unresolved_innate_spellcasting_2014(source: CatalogMonster2014) -> list[str]:
    if "Innate Spellcasting" not in source.trait_names:
        return []
    profile = source.innate_spellcasting
    if profile is None or not profile.source_complete or not profile.spells:
        return ["unparsed-source"]
    return [
        spell.name
        for spell in profile.spells
        if spell.id not in ARENA_NEUTRAL_INNATE_SPELLS
    ]
