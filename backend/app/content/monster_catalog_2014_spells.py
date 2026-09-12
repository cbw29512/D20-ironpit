from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.monster_spell_actions_2014 import SUPPORTED_DAMAGE_SPELLS_2014

# Explicit roster-loading scope: preserve every printed spell in source data, but
# non-damaging spells do not block the damage-first monster milestone. Unknown
# spells still fail closed; only names reviewed here are intentionally scoped out.
SCOPED_OUT_NON_DAMAGE_SPELLS_2014 = frozenset({
    "animal-messenger", "animate-dead", "banishment", "barkskin", "bestow-curse",
    "bless", "blur", "calm-emotions", "charm-person", "clairvoyance", "command",
    "commune", "contagion", "control-weather", "counterspell", "create-food-and-water",
    "creation", "cure-wounds", "dancing-lights", "darkness", "detect-evil-and-good",
    "detect-magic", "detect-thoughts", "disguise-self", "dispel-magic", "divination",
    "dominate-monster", "dominate-person", "dream", "druidcraft", "entangle", "fly",
    "freedom-of-movement", "geas", "globe-of-invulnerability", "greater-invisibility",
    "greater-restoration", "heroes-feast", "hold-person", "identify", "invisibility",
    "legend-lore", "lesser-restoration", "light", "locate-object", "longstrider",
    "mage-armor", "mage-hand", "mending", "mind-blank", "minor-illusion", "mirror-image",
    "misty-step", "nondetection", "pass-without-trace", "plane-shift", "power-word-stun",
    "prestidigitation", "raise-dead", "remove-curse", "resurrection", "sanctuary", "scrying",
    "shield", "shield-of-faith", "shillelagh", "silence", "sleep", "speak-with-animals",
    "spare-the-dying", "stoneskin", "suggestion", "thaumaturgy", "time-stop", "tongues",
    "teleport", "true-seeing", "wall-of-force", "water-breathing", "zone-of-truth",
})


def _regular_unresolved(source: CatalogMonster2014) -> list[str]:
    profile = source.spellcasting
    if profile is None or not profile.source_complete or not profile.spells:
        return ["unparsed-regular-spellcasting"]
    return [
        spell.name for spell in profile.spells
        if spell.id not in SCOPED_OUT_NON_DAMAGE_SPELLS_2014
        and spell.id not in SUPPORTED_DAMAGE_SPELLS_2014
    ]


def _innate_unresolved(source: CatalogMonster2014) -> list[str]:
    profile = source.innate_spellcasting
    if profile is None or not profile.source_complete or not profile.spells:
        return ["unparsed-innate-spellcasting"]
    # Innate damage resources are a separate binding tranche; do not mark a
    # damaging spell supported here until its at-will/per-day pool is compiled.
    return [spell.name for spell in profile.spells if spell.id not in SCOPED_OUT_NON_DAMAGE_SPELLS_2014]


def unresolved_spells_2014(source: CatalogMonster2014) -> list[str]:
    unresolved: list[str] = []
    if "Spellcasting" in source.trait_names:
        unresolved.extend(_regular_unresolved(source))
    if "Innate Spellcasting" in source.trait_names:
        unresolved.extend(_innate_unresolved(source))
    return list(dict.fromkeys(unresolved))
