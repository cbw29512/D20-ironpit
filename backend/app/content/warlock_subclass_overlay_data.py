from __future__ import annotations


WARLOCK_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "fiend-patron": {
        3: {"features_added": ("dark-ones-blessing", "fiend-combat-spells-2")},
        5: {"features_added": ("fiend-combat-spells-3",)},
        6: {"features_added": ("dark-ones-own-luck",)},
        7: {"features_added": ("fiend-combat-spells-4",)},
        9: {"features_added": ("fiend-combat-spells-5",)},
        10: {"features_added": ("fiendish-resilience",)},
        14: {"features_added": ("hurl-through-hell",)},
    },
    "great-old-one-patron": {
        3: {"features_added": ("awakened-mind", "great-old-one-combat-spells-2")},
        5: {"features_added": ("great-old-one-combat-spells-3",)},
        6: {"features_added": ("clairvoyant-combatant",)},
        7: {"features_added": ("great-old-one-combat-spells-4",)},
        9: {"features_added": ("great-old-one-combat-spells-5",)},
        10: {"features_added": ("eldritch-hex",)},
        14: {"features_added": ("create-thrall",)},
    },
    "celestial-patron": {
        3: {"features_added": ("healing-light", "celestial-combat-spells-2")},
        5: {"features_added": ("celestial-combat-spells-3",)},
        6: {"features_added": ("radiant-soul",)},
        7: {"features_added": ("celestial-combat-spells-4",)},
        9: {"features_added": ("celestial-combat-spells-5",)},
        10: {"features_added": ("celestial-resilience",)},
        14: {"features_added": ("searing-vengeance",)},
    },
}
