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


def _cantrip(spell_id: str, name: str, role: str, *capabilities: str) -> CanonicalSpellChoice:
    return _spell(spell_id, name, role, *capabilities, spell_level=0)


DRUID_CANTRIPS: tuple[CanonicalSpellChoice, ...] = (
    _cantrip("poison-spray", "Poison Spray", "damage", "spell-attack", "cantrip-scaling"),
    _cantrip("elementalism", "Elementalism", "utility", "arena-out-of-scope"),
    _cantrip("mending", "Mending", "utility", "arena-out-of-scope"),
)


DRUID_SPELLS: tuple[CanonicalSpellChoice, ...] = (
    _spell("healing-word", "Healing Word", "healing", "healing", "bonus-action"),
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("longstrider", "Longstrider", "buff", "modifier-stack"),
    _spell("detect-magic", "Detect Magic", "utility", "arena-out-of-scope"),
    _spell("faerie-fire", "Faerie Fire", "control", "save-modifier", "area", "concentration", min_character_level=2),
    _spell(
        "speak-with-animals",
        "Speak with Animals",
        "utility",
        "arena-out-of-scope",
        always_prepared_from_level=1,
    ),
)
