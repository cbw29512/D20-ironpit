from __future__ import annotations

from app.content.canonical_spell_choice import spell_choice as _spell


PALADIN_SPELLS = (
    _spell("cure-wounds", "Cure Wounds", "healing", "healing"),
    _spell("divine-favor", "Divine Favor", "damage", "modifier-stack", "bonus-damage"),
    _spell("bless", "Bless", "buff", "modifier-stack", "concentration", min_character_level=2),
    _spell(
        "searing-smite", "Searing Smite", "damage", "post-hit-spell",
        min_character_level=3,
    ),
    _spell(
        "thunderous-smite", "Thunderous Smite", "damage", "post-hit-spell",
        min_character_level=4,
    ),
    _spell(
        "shining-smite", "Shining Smite", "damage", "post-hit-spell",
        spell_level=2, min_character_level=5,
    ),
    _spell(
        "lesser-restoration", "Lesser Restoration", "healing",
        "condition-removal", spell_level=2, min_character_level=7,
    ),
    _spell(
        "aura-of-vitality", "Aura of Vitality", "healing", "recovery-aura",
        "concentration", spell_level=3, min_character_level=9,
    ),
    _spell(
        "blinding-smite", "Blinding Smite", "damage", "post-hit-spell",
        spell_level=3, min_character_level=9,
    ),
    _spell(
        "crusaders-mantle", "Crusader's Mantle", "damage", "weapon-damage-aura",
        "concentration", spell_level=3, min_character_level=11,
    ),
    _spell(
        "staggering-smite", "Staggering Smite", "damage", "post-hit-spell",
        spell_level=4, min_character_level=13,
    ),
    _spell(
        "aura-of-life", "Aura of Life", "healing", "recovery-aura",
        "concentration", spell_level=4, min_character_level=15,
    ),
    _spell(
        "destructive-wave", "Destructive Wave", "damage", "save-damage", "area",
        spell_level=5, min_character_level=17,
    ),
    _spell(
        "greater-restoration", "Greater Restoration", "healing", "condition-removal",
        spell_level=5, min_character_level=17,
    ),
    _spell(
        "banishing-smite", "Banishing Smite", "damage", "post-hit-spell",
        spell_level=5, min_character_level=19,
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
    _spell(
        "find-steed", "Find Steed", "utility", "arena-unavailable-summon",
        spell_level=2, min_character_level=5, always_prepared_from_level=5,
    ),
    _spell(
        "aid", "Aid", "buff", "modifier-stack",
        spell_level=2, min_character_level=5, always_prepared_from_level=5,
    ),
    _spell(
        "zone-of-truth", "Zone of Truth", "control", "arena-out-of-scope",
        spell_level=2, min_character_level=5, always_prepared_from_level=5,
    ),
    _spell(
        "beacon-of-hope", "Beacon of Hope", "buff", "modifier-stack", "concentration",
        spell_level=3, min_character_level=9, always_prepared_from_level=9,
    ),
    _spell(
        "dispel-magic", "Dispel Magic", "control", "effect-removal",
        spell_level=3, min_character_level=9, always_prepared_from_level=9,
    ),
    _spell(
        "freedom-of-movement", "Freedom of Movement", "buff", "debuff-counter",
        spell_level=4, min_character_level=13, always_prepared_from_level=13,
    ),
    _spell(
        "guardian-of-faith", "Guardian of Faith", "control", "arena-unavailable-summon",
        spell_level=4, min_character_level=13, always_prepared_from_level=13,
    ),
    _spell(
        "commune", "Commune", "utility", "arena-out-of-scope",
        spell_level=5, min_character_level=17, always_prepared_from_level=17,
    ),
    _spell(
        "flame-strike", "Flame Strike", "damage", "save-damage", "area",
        spell_level=5, min_character_level=17, always_prepared_from_level=17,
    ),
)
