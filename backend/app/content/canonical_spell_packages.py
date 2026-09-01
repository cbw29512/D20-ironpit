from __future__ import annotations

from app.content.class_spell_progression import CASTING_ABILITIES, prepared_spell_count
from app.domain.class_loadouts import CanonicalSpellChoice, CasterClassId, ClassSpellPackage


def _spell(
    spell_id: str,
    name: str,
    role: str,
    *capabilities: str,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=1,
        min_character_level=1,
        role=role,
        required_capabilities=list(capabilities),
    )


LEVEL_ONE_PACKAGES: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
    "bard": (
        _spell("charm-person", "Charm Person", "control", "charmed"),
        _spell("color-spray", "Color Spray", "control", "blinded"),
        _spell("dissonant-whispers", "Dissonant Whispers", "damage", "save-damage"),
        _spell("healing-word", "Healing Word", "healing", "healing"),
    ),
    "cleric": (
        _spell("bless", "Bless", "buff", "modifier-stack", "concentration"),
        _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
        _spell("guiding-bolt", "Guiding Bolt", "mixed", "spell-attack", "next-attack-advantage"),
        _spell("shield-of-faith", "Shield of Faith", "buff", "modifier-stack", "concentration"),
    ),
    "druid": (
        _spell("animal-friendship", "Animal Friendship", "control", "charmed"),
        _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
        _spell("faerie-fire", "Faerie Fire", "debuff", "modifier-stack", "concentration"),
        _spell("thunderwave", "Thunderwave", "damage", "save-damage", "forced-movement"),
    ),
    "paladin": (
        _spell("heroism", "Heroism", "buff", "modifier-stack", "concentration"),
        _spell("searing-smite", "Searing Smite", "mixed", "spell-buff", "ongoing-damage"),
    ),
    "ranger": (
        _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
        _spell("ensnaring-strike", "Ensnaring Strike", "mixed", "spell-buff", "restrained", "concentration"),
    ),
    "sorcerer": (
        _spell("burning-hands", "Burning Hands", "damage", "save-damage", "area"),
        _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    ),
    "warlock": (
        _spell("charm-person", "Charm Person", "control", "charmed"),
        _spell("hex", "Hex", "mixed", "modifier-stack", "bonus-damage", "concentration"),
    ),
    "wizard": (
        _spell("mage-armor", "Mage Armor", "buff", "modifier-stack"),
        _spell("magic-missile", "Magic Missile", "damage", "auto-hit-damage"),
        _spell("sleep", "Sleep", "control", "incapacitating-control"),
        _spell("thunderwave", "Thunderwave", "damage", "save-damage", "forced-movement"),
    ),
}


def build_level_one_package(class_id: CasterClassId) -> ClassSpellPackage:
    spells = list(LEVEL_ONE_PACKAGES[class_id])
    expected = prepared_spell_count(class_id, 1)
    if len(spells) != expected:
        raise ValueError(f"{class_id} level-1 package must contain exactly {expected} prepared spells.")
    return ClassSpellPackage(
        class_id=class_id,
        casting_ability=CASTING_ABILITIES[class_id],
        spells=spells,
    )
