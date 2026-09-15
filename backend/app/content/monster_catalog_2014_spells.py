from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.monster_defensive_spell_actions_2014 import SUPPORTED_DEFENSIVE_SPELLS_2014
from app.content.monster_innate_spell_actions_2014 import SUPPORTED_INNATE_ACTION_SPELLS_2014
from app.content.monster_spell_actions_2014 import SUPPORTED_DAMAGE_SPELLS_2014
from app.content.monster_spell_substitutions_2014 import ARENA_DAMAGE_SUBSTITUTIONS_2014

# Explicit roster-loading scope: preserve every printed spell in source data, but
# non-damaging spells do not block the damage-first monster milestone. Complex
# combat spells may execute a documented simpler arena damage substitution.
SCOPED_OUT_NON_DAMAGE_SPELLS_2014 = frozenset({
    "animal-messenger", "animate-dead", "banishment", "barkskin", "bestow-curse",
    "bless", "blur", "calm-emotions", "charm-person", "clairvoyance", "command",
    "commune", "conjure-elemental", "contagion", "control-weather", "counterspell",
    "create-food-and-water", "creation", "cure-wounds", "dancing-lights", "darkness",
    "detect-evil-and-good", "detect-magic", "detect-thoughts", "dimension-door", "disguise-self",
    "dispel-evil-and-good", "dispel-magic", "divination", "dominate-monster", "dominate-person",
    "dream", "druidcraft", "enlarge-reduce", "entangle", "feather-fall", "fly", "freedom-of-movement",
    "gaseous-form", "geas", "globe-of-invulnerability", "goodberry", "greater-invisibility",
    "greater-restoration", "heroes-feast", "hold-person", "identify", "invisibility", "legend-lore",
    "lesser-restoration", "light", "locate-object", "longstrider", "mage-armor", "mage-hand",
    "major-image", "mending", "mind-blank", "minor-illusion", "mirror-image", "misty-step",
    "nondetection", "pass-without-trace", "plane-shift", "polymorph", "power-word-stun",
    "prestidigitation", "protection-from-poison", "raise-dead", "remove-curse", "resurrection",
    "sanctuary", "scrying", "shield", "shield-of-faith", "shillelagh", "silence", "sleep",
    "speak-with-animals", "spare-the-dying", "stoneskin", "suggestion", "thaumaturgy",
    "time-stop", "tongues", "teleport", "true-seeing", "wall-of-force", "water-breathing", "wind-walk",
    "zone-of-truth",
})


def _regular_unresolved(source: CatalogMonster2014) -> list[str]:
    profile = source.spellcasting
    if profile is None or not profile.source_complete or not profile.spells:
        return ["unparsed-regular-spellcasting"]
    supported = (
        SCOPED_OUT_NON_DAMAGE_SPELLS_2014
        | SUPPORTED_DAMAGE_SPELLS_2014
        | SUPPORTED_DEFENSIVE_SPELLS_2014
        | ARENA_DAMAGE_SUBSTITUTIONS_2014
    )
    return [spell.name for spell in profile.spells if spell.id not in supported]


def _innate_unresolved(source: CatalogMonster2012014) -> list[str]:
    profile = source.innate_spellcasting
    if profile is None or not profile.source_complete or not profile.spells:
        return ["unparsed-innate-spellcasting"]
    supported = (
        SCOPED_OUT_NON_DAMAGE_SPELLS_2014
        | SUPPORTED_INNATE_ACTION_SPELLS_2014
        | ARENA_DAMAGE_SUBSTITUTIONS_2014
    )
    return [spell.name for spell in profile.spells if spell.id not in supported]


def unresolved_spells_2014(source: CatalogMonster2014) -> list[str]:
    unresolved: list[str] = []
    if "Spellcasting" in source.trait_names:
        unresolved.extend(_regular_unresolved(source))
    if "Innate Spellcasting" in source.trait_names:
        unresolved.extend(_innate_unresolved(source))
    return list(dict.fromkeys(unresolved))
