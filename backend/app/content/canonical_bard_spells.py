from __future__ import annotations

from app.content.canonical_bard_high_spells import BARD_HIGH_LEVEL_SPELLS
from app.domain.class_loadouts import CanonicalSpellChoice


def _spell(
    spell_id: str,
    name: str,
    role: str,
    *capabilities: str,
    spell_level: int = 1,
    min_character_level: int = 1,
    always_prepared_from_level: int | None = None,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=spell_level,
        min_character_level=min_character_level,
        always_prepared_from_level=always_prepared_from_level,
        role=role,
        required_capabilities=list(capabilities),
    )


def _cantrip(
    spell_id: str,
    name: str,
    role: str,
    *capabilities: str,
    min_character_level: int = 1,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=0,
        min_character_level=min_character_level,
        role=role,
        required_capabilities=list(capabilities),
    )


BARD_CANTRIPS: tuple[CanonicalSpellChoice, ...] = (
    _cantrip("dancing-lights", "Dancing Lights", "utility", "arena-out-of-scope"),
    _cantrip("mage-hand", "Mage Hand", "utility", "arena-out-of-scope"),
    _cantrip(
        "message",
        "Message",
        "utility",
        "arena-out-of-scope",
        min_character_level=4,
    ),
    _cantrip(
        "prestidigitation",
        "Prestidigitation",
        "utility",
        "arena-out-of-scope",
        min_character_level=10,
    ),
)


BARD_SPELLS: tuple[CanonicalSpellChoice, ...] = (
    _spell("healing-word", "Healing Word", "healing", "healing"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("comprehend-languages", "Comprehend Languages", "utility", "arena-out-of-scope"),
    _spell("identify", "Identify", "utility", "arena-out-of-scope"),
    _spell(
        "shatter",
        "Shatter",
        "damage",
        "save-damage",
        "area",
        spell_level=2,
        min_character_level=3,
    ),
    _spell(
        "knock",
        "Knock",
        "utility",
        "arena-out-of-scope",
        spell_level=2,
        min_character_level=4,
    ),
    _spell(
        "mass-healing-word",
        "Mass Healing Word",
        "healing",
        "healing",
        spell_level=3,
        min_character_level=5,
    ),
    _spell(
        "sending",
        "Sending",
        "utility",
        "arena-out-of-scope",
        spell_level=3,
        min_character_level=5,
    ),
    _spell(
        "dispel-magic",
        "Dispel Magic",
        "control",
        "effect-removal",
        spell_level=3,
        min_character_level=6,
    ),
    _spell(
        "bless",
        "Bless",
        "buff",
        "modifier-stack",
        "concentration",
        "magical-discoveries",
        min_character_level=6,
        always_prepared_from_level=6,
    ),
    _spell(
        "guiding-bolt",
        "Guiding Bolt",
        "damage",
        "spell-attack",
        "next-attack-advantage",
        "magical-discoveries",
        min_character_level=6,
        always_prepared_from_level=6,
    ),
    _spell(
        "greater-invisibility",
        "Greater Invisibility",
        "buff",
        "condition",
        "concentration",
        spell_level=4,
        min_character_level=7,
    ),
    _spell(
        "tongues",
        "Tongues",
        "utility",
        "arena-out-of-scope",
        spell_level=3,
        min_character_level=8,
    ),
    _spell(
        "mass-cure-wounds",
        "Mass Cure Wounds",
        "healing",
        "healing",
        spell_level=5,
        min_character_level=9,
    ),
    _spell(
        "raise-dead",
        "Raise Dead",
        "utility",
        "arena-out-of-scope",
        spell_level=5,
        min_character_level=9,
    ),
    *BARD_HIGH_LEVEL_SPELLS,

)
