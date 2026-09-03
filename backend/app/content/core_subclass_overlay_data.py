from __future__ import annotations


CORE_SUBCLASS_DELTA_DATA: dict[str, tuple[str, dict[int, dict[str, tuple[str, ...]]]]] = {
    "college-lore": ("bard", {
        3: {"features_added": ("cutting-words",), "arena_ignored": ("lore-bonus-proficiencies",)},
        6: {"features_added": ("magical-discoveries",)}, 14: {"features_added": ("peerless-skill",)},
    }),
    "life-domain": ("cleric", {
        3: {"features_added": ("disciple-of-life", "preserve-life")},
        6: {"features_added": ("blessed-healer",)}, 17: {"features_added": ("supreme-healing",)},
    }),
    "circle-land": ("druid", {
        3: {"features_added": ("lands-aid", "land-arid-spells")},
        6: {"features_added": ("natural-recovery",)}, 10: {"features_added": ("natures-ward-fire",)},
        14: {"features_added": ("natures-sanctuary",)},
    }),
    "champion": ("fighter", {
        3: {"features_added": ("improved-critical", "remarkable-athlete")},
        7: {"features_added": ("great-weapon-fighting",)}, 10: {"features_added": ("heroic-warrior",)},
        15: {"features_added": ("superior-critical",), "features_removed": ("improved-critical",)},
        18: {"features_added": ("survivor-defy-death", "survivor-heroic-rally")},
    }),
    "draconic-sorcery": ("sorcerer", {
        3: {"features_added": ("draconic-resilience",)}, 6: {"features_added": ("elemental-affinity-fire",)},
        14: {"features_added": ("dragon-wings",)}, 18: {"features_added": ("dragon-companion",)},
    }),
    "fiend-patron": ("warlock", {
        3: {"features_added": ("dark-ones-blessing", "fiend-combat-spells-2")},
        5: {"features_added": ("fiend-combat-spells-3",)}, 6: {"features_added": ("dark-ones-own-luck",)},
        7: {"features_added": ("fiend-combat-spells-4",)}, 9: {"features_added": ("fiend-combat-spells-5",)},
        10: {"features_added": ("fiendish-resilience",)}, 14: {"features_added": ("hurl-through-hell",)},
    }),
}
