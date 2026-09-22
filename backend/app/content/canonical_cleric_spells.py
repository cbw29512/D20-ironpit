from __future__ import annotations

from app.domain.class_loadouts import CanonicalSpellChoice


def _spell(
    spell_id: str, name: str, spell_level: int, role: str, min_level: int,
    *capabilities: str, always_prepared_from_level: int | None = None,
) -> CanonicalSpellChoice:
    return CanonicalSpellChoice(
        id=spell_id,
        name=name,
        spell_level=spell_level,
        min_character_level=min_level,
        always_prepared_from_level=always_prepared_from_level,
        role=role,
        required_capabilities=list(capabilities),
    )


CLERIC_CANTRIPS = (
    _spell("sacred-flame", "Sacred Flame", 0, "damage", 1, "save-damage", "cantrip-scaling"),
    _spell("light", "Light", 0, "utility", 1, "arena-out-of-scope"),
    _spell("thaumaturgy", "Thaumaturgy", 0, "utility", 1, "arena-out-of-scope"),
    _spell("mending", "Mending", 0, "utility", 4, "arena-out-of-scope"),
    _spell("spare-the-dying", "Spare the Dying", 0, "healing", 10, "arena-out-of-scope"),
)


CLERIC_SPELLS = (
    _spell("bless", "Bless", 1, "buff", 1, "modifier-stack", "concentration", always_prepared_from_level=3),
    _spell("cure-wounds", "Cure Wounds", 1, "healing", 1, "healing", always_prepared_from_level=3),
    _spell("guiding-bolt", "Guiding Bolt", 1, "mixed", 1, "spell-attack", "next-attack-advantage"),
    _spell("shield-of-faith", "Shield of Faith", 1, "buff", 1, "modifier-stack", "concentration"),
    _spell("healing-word", "Healing Word", 1, "healing", 2, "healing", "bonus-action"),
    _spell("detect-magic", "Detect Magic", 1, "utility", 3, "arena-out-of-scope"),
    _spell("create-or-destroy-water", "Create or Destroy Water", 1, "utility", 3, "arena-out-of-scope"),
    _spell("augury", "Augury", 2, "utility", 3, "arena-out-of-scope"),
    _spell("inflict-wounds", "Inflict Wounds", 1, "damage", 4, "save-damage"),
    _spell("aid", "Aid", 2, "buff", 3, "max-hp-increase", always_prepared_from_level=3),
    _spell(
        "lesser-restoration", "Lesser Restoration", 2, "healing", 3,
        "condition-removal", "bonus-action", always_prepared_from_level=3,
    ),
    _spell("dispel-magic", "Dispel Magic", 3, "utility", 5, "effect-removal"),
    _spell("create-food-and-water", "Create Food and Water", 3, "utility", 5, "arena-out-of-scope"),
    _spell("daylight", "Daylight", 3, "utility", 6, "arena-out-of-scope"),
    _spell(
        "mass-healing-word", "Mass Healing Word", 3, "healing", 5,
        "healing", "bonus-action", "multi-target-healing", always_prepared_from_level=5,
    ),
    _spell("revivify", "Revivify", 3, "healing", 5, "arena-out-of-scope", always_prepared_from_level=5),
    _spell("aura-of-life", "Aura of Life", 4, "healing", 7, "arena-out-of-scope", always_prepared_from_level=7),
    _spell("death-ward", "Death Ward", 4, "healing", 7, "arena-out-of-scope", always_prepared_from_level=7),
    _spell("prayer-of-healing", "Prayer of Healing", 2, "healing", 7, "arena-out-of-scope"),
    _spell("guardian-of-faith", "Guardian of Faith", 4, "damage", 8, "arena-out-of-scope"),
    _spell("flame-strike", "Flame Strike", 5, "damage", 9, "arena-out-of-scope"),
    _spell("insect-plague", "Insect Plague", 5, "damage", 9, "arena-out-of-scope"),
    _spell("contagion", "Contagion", 5, "damage", 10, "arena-out-of-scope"),
    _spell("heal", "Heal", 6, "healing", 11, "arena-out-of-scope"),
    _spell("fire-storm", "Fire Storm", 7, "damage", 13, "arena-out-of-scope"),
    _spell(
        "greater-restoration", "Greater Restoration", 5, "healing", 9,
        "arena-out-of-scope", always_prepared_from_level=9,
    ),
    _spell(
        "mass-cure-wounds", "Mass Cure Wounds", 5, "healing", 9,
        "healing", "multi-target-healing", always_prepared_from_level=9,
    ),
)
