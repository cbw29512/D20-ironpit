from __future__ import annotations

from app.content.canonical_bard_spells import BARD_CANTRIPS, BARD_SPELLS
from app.content.canonical_cleric_spells import CLERIC_CANTRIPS, CLERIC_SPELLS
from app.content.canonical_druid_spells import DRUID_CANTRIPS, DRUID_SPELLS
from app.content.class_spell_progression import CASTING_ABILITIES, max_spell_level, prepared_spell_count
from app.domain.class_loadouts import CanonicalSpellChoice, CasterClassId, ClassSpellPackage


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


CANONICAL_CANTRIPS: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
    "bard": BARD_CANTRIPS,
    "cleric": CLERIC_CANTRIPS,
    "druid": DRUID_CANTRIPS,
}


CANONICAL_SPELLS: dict[CasterClassId, tuple[CanonicalSpellChoice, ...]] = {
    "bard": BARD_SPELLS,
    "cleric": CLERIC_SPELLS,
    "druid": DRUID_SPELLS,
    "paladin": (
        _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
        _spell("divine-favor", "Divine Favor", "damage", "modifier-stack", "bonus-damage"),
        _spell("bless", "Bless", "buff", "modifier-stack", "concentration", min_character_level=2),
        _spell(
            "searing-smite", "Searing Smite", "damage", "arena-out-of-scope",
            min_character_level=3,
        ),
        _spell(
            "divine-smite", "Divine Smite", "damage", "post-hit-resource-damage",
            min_character_level=2, always_prepared_from_level=2,
        ),
        _spell(
            "protection-from-evil-and-good", "Protection from Evil and Good", "buff",
            "modifier-stack", "concentration", min_character_level=3, always_prepared_from_level=3,
        ),
        _spell(
            "shield-of-faith", "Shield of Faith", "buff", "modifier-stack", "concentration",
            min_character_level=3, always_prepared_from_level=3,
        ),
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
