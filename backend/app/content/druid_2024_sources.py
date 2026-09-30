from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def druid_profile_source_references(level: int) -> list[str]:
    try:
        refs = [
            "D&D Beyond Basic Rules 2024: Druid — Core Traits, Spellcasting, Druidic, Primal Order",
            "D&D Beyond Basic Rules 2024: Character Origins — Elf (Wood Elf), Acolyte",
            "D&D Beyond Basic Rules 2024: Feats — Magic Initiate",
            "D&D Beyond Basic Rules 2024: Equipment — Leather Armor, Shield, Sickle",
            "D&D Beyond Basic Rules 2024: Spells — Poison Spray, Healing Word, Cure Wounds, Longstrider, Faerie Fire",
        ]
        additions = (
            (2, "D&D Beyond Basic Rules 2024: Druid 2 — Wild Shape, Wild Companion"),
            (3, "D&D Beyond Basic Rules 2024: Circle of the Land 3 — Land's Aid, Circle Spells (Arid)"),
            (4, "D&D Beyond Basic Rules 2024: Druid 4 — Ability Score Improvement; Starry Wisp"),
            (4, "D&D Beyond Basic Rules 2024: Spells — Detect Poison and Disease"),
            (5, "D&D Beyond Basic Rules 2024: Druid 5 — Wild Resurgence; level 3 spell slots"),
            (6, "D&D Beyond Basic Rules 2024: Circle of the Land 6 — Natural Recovery"),
            (6, "D&D Beyond Basic Rules 2024: Spells — Aid"),
            (7, "D&D Beyond Basic Rules 2024: Druid 7 — Elemental Fury: Potent Spellcasting"),
            (7, "D&D Beyond Basic Rules 2024: Circle of the Land 7 — Arid Circle Spell: Blight"),
            (7, "D&D Beyond Basic Rules 2024: Spells — Divination"),
            (8, "D&D Beyond Basic Rules 2024: Druid 8 — Ability Score Improvement; Wild Shape improvement"),
            (8, "D&D Beyond Basic Rules 2024: Spells — Freedom of Movement"),
            (9, "D&D Beyond Basic Rules 2024: Druid 9 — level 5 spell slots"),
            (9, "D&D Beyond Basic Rules 2024: Spells — Cone of Cold, Mass Cure Wounds"),
            (9, "D&D Beyond Basic Rules 2024: Circle of the Land 9 — Arid Circle Spell: Wall of Stone"),
            (10, "D&D Beyond Basic Rules 2024: Circle of the Land 10 — Nature's Ward"),
            (10, "D&D Beyond Basic Rules 2024: Spells — Thunderwave"),
            (11, "D&D Beyond Basic Rules 2024: Druid 11 — level 6 spell slot"),
            (11, "D&D Beyond Basic Rules 2024: Spells — Heal"),
            (12, "D&D Beyond Basic Rules 2024: Druid 12 — Ability Score Improvement (+2 Charisma)"),
            (13, "D&D Beyond Basic Rules 2024: Druid 13 — level 7 spell slot"),
            (13, "D&D Beyond Basic Rules 2024: Spells — Fire Storm"),
            (14, "D&D Beyond Basic Rules 2024: Circle of the Land 14 — Nature's Sanctuary"),
            (14, "D&D Beyond Basic Rules 2024: Circle of the Land 14 — Land's Aid scales to 4d6"),
            (15, "D&D Beyond Basic Rules 2024: Druid 15 — Improved Elemental Fury: Potent Spellcasting"),
            (15, "D&D Beyond Basic Rules 2024: Druid 15 — level 8 spell slot; Spells — Sunburst"),
            (16, "D&D Beyond Basic Rules 2024: Druid 16 — Ability Score Improvement (+2 Charisma)"),
            (17, "D&D Beyond Basic Rules 2024: Druid 17 — level 9 spell slot; Spells — Foresight"),
        )
        refs.extend(reference for minimum_level, reference in additions if level >= minimum_level)
        return refs
    except Exception:
        logger.exception("Failed to build 2024 Druid profile source references at level %s.", level)
        raise


def druid_runtime_source_reference(level: int) -> str:
    try:
        parts = [
            "Wood Elf", "Acolyte", "Druid", "Primal Order: Magician",
            "Poison Spray", "Healing Word", "Cure Wounds", "Longstrider", "Equipment",
        ]
        additions = (
            (2, ("Faerie Fire", "Wild Shape")),
            (3, ("Lesser Restoration", "Circle of the Land (Arid)", "Blur", "Burning Hands", "Fire Bolt", "Land's Aid")),
            (4, ("Starry Wisp", "Detect Poison and Disease")),
            (5, ("Fireball", "Dispel Magic", "Water Breathing", "Wild Resurgence")),
            (6, ("Natural Recovery", "Aid")),
            (7, ("Elemental Fury: Potent Spellcasting", "Blight", "Divination")),
            (8, ("Ability Score Improvement", "Wild Shape Improvement", "Freedom of Movement")),
            (9, ("Cone of Cold", "Mass Cure Wounds", "Wall of Stone")),
            (10, ("Nature's Ward", "Thunderwave")),
            (11, ("Heal",)),
            (12, ("Ability Score Improvement",)),
            (13, ("Fire Storm",)),
            (14, ("Nature's Sanctuary", "Land's Aid Improvement")),
            (15, ("Improved Elemental Fury: Potent Spellcasting", "Sunburst")),
            (16, ("Ability Score Improvement",)),
            (17, ("Foresight",)),
        )
        for minimum_level, names in additions:
            if level >= minimum_level:
                parts.extend(names)
        return "D&D Beyond Basic Rules 2024: " + ", ".join(parts)
    except Exception:
        logger.exception("Failed to build 2024 Druid runtime source reference at level %s.", level)
        raise
