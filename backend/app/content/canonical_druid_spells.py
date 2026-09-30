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
        "speak-with-animals",
        "Speak with Animals",
        "utility",
        "arena-out-of-scope",
        always_prepared_from_level=1,
    ),
)
