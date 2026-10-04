from __future__ import annotations

from app.content.canonical_bard_spells import BARD_CANTRIPS, BARD_SPELLS
from app.content.canonical_cleric_spells import CLERIC_CANTRIPS, CLERIC_SPELLS
from app.content.canonical_druid_spells import DRUID_CANTRIPS, DRUID_SPELLS
from app.content.canonical_paladin_spells import PALADIN_SPELLS
from app.content.canonical_spell_choice import spell_choice as _spell
from app.content.class_spell_progression import CASTING_ABILITIES, max_spell_level, prepared_spell_count
from app.domain.class_loadouts import CanonicalSpellChoice, CasterClassId, ClassSpellPackage


CANONICAL_CANTRIPS: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
    "bard": BARD_CANTRIPS,
    "cleric": CLERIC_CANTRIPS,
    "druid": DRUID_CANTRIPS,
}


CANONICAL_SPELLS: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
    "bard": BARD_SPELLS,
    "cleric": CLERIC_SPELLS,
    "druid": DRUID_SPELLS,
    "paladin": PALADIN_SPELLS,
    "ranger": (
        _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
        _spell("ensnaring-strike", "Ensnaring Strike", "mixed", "spell-buff", "restrained", "concentration"),
        _spell("longstrider", "Longstrider", "buff", "speed-modifier", min_character_level=2),
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
    if class_id in {"cleric", "druid"}:
        expected_cantrips = (
            3 + int(character_level >= 4) + int(character_level >= 10)
            if class_id == "cleric"
            else 3 + int(character_level >= 4) + int(character_level >= 10)
        )
        if len(cantrips) != expected_cantrips:
            raise ValueError(
                f"{class_id.title()} level {character_level} canonical package needs {expected_cantrips} cantrips, "
                f"has {len(cantrips)}."
            )
    return ClassSpellPackage(
        class_id=class_id,
        casting_ability=CASTING_ABILITIES[class_id],
        cantrips=cantrips,
        spells=prepared[:expected],
        always_prepared_spells=always_prepared,
    )


def build_level_one_package(class_id: CasterClassId) -> ClassSpellPackage:
    return build_class_spell_package(class_id, 1)
