from __future__ import annotations

from app.domain.class_loadouts import CanonicalSpellChoice


def _spell(
    spell_id: str,
    name: str,
    role: str,
    *capabilities: str,
    spell_level: int,
    min_character_level: int,
    always_prepared_from_level: int | None = None,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=spell_level,
        min_character_level=min_character_level,
        role=role,
        required_capabilities=list(capabilities),
        always_prepared_from_level=always_prepared_from_level,
    )


BARD_HIGH_LEVEL_SPELLS: tuple[CanonicalSpellChoice, ...] = (
    _spell(
        "fireball", "Fireball", "damage",
        "save-damage", "area", "magical-secrets",
        spell_level=3, min_character_level=10,
    ),
    _spell(
        "disintegrate", "Disintegrate", "damage",
        "save-damage", "magical-secrets",
        spell_level=6, min_character_level=11,
    ),
    _spell(
        "finger-of-death", "Finger of Death", "damage",
        "save-damage", "magical-secrets",
        spell_level=7, min_character_level=13,
    ),
    _spell(
        "sunburst", "Sunburst", "damage",
        "save-damage", "area", "condition", "magical-secrets",
        spell_level=8, min_character_level=15,
    ),
    _spell(
        "power-word-kill", "Power Word Kill", "damage",
        "hp-threshold-instant-death", "fallback-damage", "magical-secrets",
        spell_level=9, min_character_level=17, always_prepared_from_level=20,
    ),
    _spell(
        "teleport", "Teleport", "utility", "arena-out-of-scope",
        spell_level=7, min_character_level=18,
    ),
    _spell(
        "cone-of-cold", "Cone of Cold", "damage",
        "save-damage", "area", "magical-secrets",
        spell_level=5, min_character_level=19,
    ),
    _spell(
        "circle-of-death", "Circle of Death", "damage",
        "save-damage", "area", "magical-secrets",
        spell_level=6, min_character_level=20,
    ),
    _spell(
        "legend-lore", "Legend Lore", "utility",
        "arena-out-of-scope",
        spell_level=5, min_character_level=20,
    ),
    _spell(
        "power-word-heal", "Power Word Heal", "healing",
        "healing", "condition-removal", "words-of-creation",
        spell_level=9, min_character_level=20, always_prepared_from_level=20,
    ),
)
