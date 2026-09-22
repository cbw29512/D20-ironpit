from __future__ import annotations

from app.content.class_spell_progression import CASTING_ABILITIES, max_spell_level, prepared_spell_count
from app.domain.class_loadouts import CanonicalSpellChoice, CasterClassId, ClassSpellPackage


def _spell(
    spell_id: str, name: str, role: str, *capabilities: str, always_prepared_from_level: int | None = None,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=1, min_character_level=1,
        always_prepared_from_level=always_prepared_from_level,
        role=role, required_capabilities=list(capabilities),
    )


def _later_spell(
    spell_id: str, name: str, spell_level: int, role: str, min_character_level: int,
    *capabilities: str, always_prepared_from_level: int | None = None,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=spell_level, min_character_level=min_character_level,
        always_prepared_from_level=always_prepared_from_level,
        role=role, required_capabilities=list(capabilities),
    )


def _cantrip(spell_id: str, name: str, role: str, *capabilities: str) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=0, min_character_level=1,
        role=role, required_capabilities=list(capabilities),
    )


def _later_cantrip(
    spell_id: str, name: str, role: str, min_character_level: int, *capabilities: str,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id, name=name, spell_level=0, min_character_level=min_character_level,
        role=role, required_capabilities=list(capabilities),
    )


CANONICAL_CANTRIPS: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
    "cleric": (
        _cantrip("sacred-flame", "Sacred Flame", "damage", "save-damage", "cantrip-scaling"),
        _cantrip("light", "Light", "utility", "arena-out-of-scope"),
        _cantrip("thaumaturgy", "Thaumaturgy", "utility", "arena-out-of-scope"),
        _later_cantrip("mending", "Mending", "utility", 4, "arena-out-of-scope"),
        _later_cantrip("spare-the-dying", "Spare the Dying", "healing", 10, "arena-out-of-scope"),
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
        _spell("bless", "Bless", "buff", "modifier-stack", "concentration", always_prepared_from_level=3),
        _spell("cure-wounds", "Cure Wounds", "healing", "healing", always_prepared_from_level=3),
        _spell("guiding-bolt", "Guiding Bolt", "mixed", "spell-attack", "next-attack-advantage"),
        _spell("shield-of-faith", "Shield of Faith", "buff", "modifier-stack", "concentration"),
        _later_spell("healing-word", "Healing Word", 1, "healing", 2, "healing", "bonus-action"),
        _later_spell("detect-magic", "Detect Magic", 1, "utility", 3, "arena-out-of-scope"),
        _later_spell("create-or-destroy-water", "Create or Destroy Water", 1, "utility", 3, "arena-out-of-scope"),
        _later_spell("augury", "Augury", 2, "utility", 3, "arena-out-of-scope"),
        _later_spell("inflict-wounds", "Inflict Wounds", 1, "damage", 4, "save-damage"),
        _later_spell("aid", "Aid", 2, "buff", 3, "max-hp-increase", always_prepared_from_level=3),
        _later_spell(
            "lesser-restoration", "Lesser Restoration", 2, "healing", 3,
            "condition-removal", "bonus-action", always_prepared_from_level=3,
        ),
        _later_spell(
            "dispel-magic", "Dispel Magic", 3, "utility", 5,
            "effect-removal",
        ),
        _later_spell(
            "create-food-and-water", "Create Food and Water", 3, "utility", 5,
            "arena-out-of-scope",
        ),
        _later_spell(
            "daylight", "Daylight", 3, "utility", 6,
            "arena-out-of-scope",
        ),
        _later_spell(
            "mass-healing-word", "Mass Healing Word", 3, "healing", 5,
            "healing", "bonus-action", "multi-target-healing", always_prepared_from_level=5,
        ),
        _later_spell(
            "revivify", "Revivify", 3, "healing", 5,
            "arena-out-of-scope", always_prepared_from_level=5,
        ),
        _later_spell(
            "aura-of-life", "Aura of Life", 4, "healing", 7,
            "arena-out-of-scope", always_prepared_from_level=7,
        ),
        _later_spell(
            "death-ward", "Death Ward", 4, "healing", 7,
            "arena-out-of-scope", always_prepared_from_level=7,
        ),
        _later_spell(
            "prayer-of-healing", "Prayer of Healing", 2, "healing", 7,
            "arena-out-of-scope",
        ),
        _later_spell(
            "guardian-of-faith", "Guardian of Faith", 4, "damage", 8,
            "arena-out-of-scope",
        ),
        _later_spell(
            "flame-strike", "Flame Strike", 5, "damage", 9,
            "arena-out-of-scope",
        ),
        _later_spell(
            "insect-plague", "Insect Plague", 5, "damage", 9,
            "arena-out-of-scope",
        ),
        _later_spell(
            "contagion", "Contagion", 5, "damage", 10,
            "arena-out-of-scope",
        ),
        _later_spell(
            "greater-restoration", "Greater Restoration", 5, "healing", 9,
            "arena-out-of-scope", always_prepared_from_level=9,
        ),
        _later_spell(
            "mass-cure-wounds", "Mass Cure Wounds", 5, "healing", 9,
            "healing", "multi-target-healing", always_prepared_from_level=9,
        ),
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
    eligible = [
        spell for spell in CANONICAL_SPELLS[class_id]
        if spell.min_character_level <= character_level and spell.spell_level <= maximum
    ]
    always_prepared = [
        spell for spell in eligible
        if spell.always_prepared_from_level is not None and character_level >= spell.always_prepared_from_level
    ]
    prepared = [spell for spell in eligible if spell not in always_prepared]
    if len(prepared) < expected:
        raise ValueError(
            f"{class_id} level {character_level} canonical package is incomplete: "
            f"needs {expected} prepared spells, has {len(prepared)}."
        )
    cantrips = [
        spell for spell in CANONICAL_CANTRIPS.get(class_id, ())
        if spell.min_character_level <= character_level
    ]
    if class_id == "cleric":
        expected_cantrips = 3 + int(character_level >= 4) + int(character_level >= 10)
        if len(cantrips) != expected_cantrips:
            raise ValueError(
                f"Cleric level {character_level} canonical package needs {expected_cantrips} cantrips, "
                f"has {len(cantrips)}."
            )
    return ClassSpellPackage(
        class_id=class_id, casting_ability=CASTING_ABILITIES[class_id],
        cantrips=cantrips, spells=prepared[:expected], always_prepared_spells=always_prepared,
    )


def build_level_one_package(class_id: CasterClassId) -> ClassSpellPackage:
    return build_class_spell_package(class_id, 1)
