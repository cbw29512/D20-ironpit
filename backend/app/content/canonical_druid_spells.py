from __future__ import annotations

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
    return _spell(
        spell_id, name, role, *capabilities,
        spell_level=0, min_character_level=min_character_level,
    )


DRUID_CANTRIPS: tuple[CanonicalSpellChoice, ...] = (
    _cantrip("poison-spray", "Poison Spray", "damage", "spell-attack", "cantrip-scaling"),
    _cantrip("elementalism", "Elementalism", "utility", "arena-out-of-scope"),
    _cantrip("mending", "Mending", "utility", "arena-out-of-scope"),
    _cantrip(
        "starry-wisp", "Starry Wisp", "damage",
        "spell-attack", "cantrip-scaling", "invisibility-benefits-suppressed",
        min_character_level=4,
    ),
    _cantrip(
        "thunderclap", "Thunderclap", "damage",
        "save-damage", "area", "cantrip-scaling",
        min_character_level=10,
    ),
)


DRUID_SPELLS: tuple[CanonicalSpellChoice, ...] = (
    _spell("healing-word", "Healing Word", "healing", "healing", "bonus-action"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("longstrider", "Longstrider", "buff", "modifier-stack"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("faerie-fire", "Faerie Fire", "control", "save-modifier", "area", "concentration", min_character_level=2),
    _spell("lesser-restoration", "Lesser Restoration", "healing", "condition-removal", "bonus-action", spell_level=2, min_character_level=3),
    _spell(
        "detect-poison-disease", "Detect Poison and Disease", "utility",
        "arena-out-of-scope", min_character_level=4,
    ),
    _spell(
        "dispel-magic", "Dispel Magic", "control",
        "effect-removal", spell_level=3, min_character_level=5,
    ),
    _spell(
        "water-breathing", "Water Breathing", "utility",
        "arena-out-of-scope", spell_level=3, min_character_level=5,
    ),
    _spell(
        "aid", "Aid", "buff", "max-hp-increase",
        spell_level=2, min_character_level=6,
    ),
    _spell(
        "divination", "Divination", "utility", "arena-out-of-scope",
        spell_level=4, min_character_level=7,
    ),
    _spell(
        "freedom-of-movement", "Freedom of Movement", "buff", "debuff-counter",
        spell_level=4, min_character_level=8,
    ),
    _spell(
        "cone-of-cold", "Cone of Cold", "damage", "save-damage", "area",
        spell_level=5, min_character_level=9,
    ),
    _spell(
        "mass-cure-wounds", "Mass Cure Wounds", "healing", "healing", "multi-target-healing",
        spell_level=5, min_character_level=9,
    ),
    _spell(
        "thunderwave", "Thunderwave", "damage", "save-damage", "area", "forced-movement",
        spell_level=1, min_character_level=10,
    ),
    _spell(
        "heal", "Heal", "healing", "healing", "condition-removal",
        spell_level=6, min_character_level=11,
    ),
    _spell(
        "fire-storm", "Fire Storm", "damage", "arena-out-of-scope",
        spell_level=7, min_character_level=13,
    ),
    _spell(
        "sunburst", "Sunburst", "damage", "save-damage", "area", "condition",
        spell_level=8, min_character_level=15,
    ),
    _spell(
        "foresight", "Foresight", "buff", "d20-test-advantage", "attacks-against-disadvantage",
        spell_level=9, min_character_level=17,
    ),
    _spell(
        "barkskin", "Barkskin", "buff", "modifier-stack",
        spell_level=2, min_character_level=18,
    ),
    _spell(
        "regenerate", "Regenerate", "healing", "arena-out-of-scope",
        spell_level=7, min_character_level=19,
    ),
    _spell(
        "ice-storm", "Ice Storm", "damage", "arena-out-of-scope",
        spell_level=4, min_character_level=20,
    ),
    _spell(
        "speak-with-animals",
        "Speak with Animals",
        "utility",
        "arena-out-of-scope",
        always_prepared_from_level=1,
    ),
)
