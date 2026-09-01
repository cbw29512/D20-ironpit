from __future__ import annotations

from app.content.class_spell_progression import CASTING_ABILITIES, max_spell_level, prepared_spell_count
from app.domain.class_loadouts import CanonicalSpellChoice, CasterClassId, ClassSpellPackage


def _spell(spell_id: str, name: str, role: str, *capabilities: str) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=1, min_character_level=1,
        role=role, required_capabilities=list(capabilities),
    )


def _later_spell(
    spell_id: str, name: str, role: str, min_character_level: int, *capabilities: str,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=1, min_character_level=min_character_level,
        role=role, required_capabilities=list(capabilities),
    )


def _cantrip(spell_id: str, name: str, role: str, *capabilities: str) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=0, min_character_level=1,
        role=role, required_capabilities=list(capabilities),
    )


CANONICAL_CANTRIPS: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
    "cleric": (
        _cantrip("sacred-flame", "Sacred Flame", "damage", "save-damage", "cantrip-scaling"),
        _cantrip("light", "Light", "utility", "arena-out-of-scope"),
        _cantrip("thaumaturgy", "Thaumaturgy", "utility", "arena-out-of-scope"),
    ),
}


CANONICAL_SPELLS: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
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
        _later_spell("healing-word", "Healing Word", "healing", 2, "healing", "bonus-action"),
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


def build_class_spell_package(class_id: CasterClassId, character_level: int) -> ClassSpellPackage:
    expected = prepared_spell_count(class_id, character_level)
    maximum = max_spell_level(class_id, character_level)
    spells = [
        spell for spell in CANONICAL_SPELLS[class_id]
        if spell.min_character_level <= character_level and spell.spell_level <= maximum
    ]
    if len(spells) < expected:
        raise ValueError(
            f"{class_id} level {character_level} canonical package is incomplete: "
            f"needs {expected} prepared spells, has {len(spells)}."
        )
    cantrips = list(CANONICAL_CANTRIPS.get(class_id, ()))
    if class_id == "cleric" and character_level <= 3 and len(cantrips) != 3:
        raise ValueError("Cleric levels 1-3 canonical package must retain exactly three chosen cantrips.")
    return ClassSpellPackage(
        class_id=class_id, casting_ability=CASTING_ABILITIES[class_id],
        cantrips=cantrips, spells=spells[:expected],
    )


def build_level_one_package(class_id: CasterClassId) -> ClassSpellPackage:
    return build_class_spell_package(class_id, 1)
