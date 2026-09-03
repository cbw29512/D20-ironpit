from __future__ import annotations


RANGER_SUBCLASS_SPELLS: dict[str, dict[int, tuple[str, ...]]] = {
    "gloom-stalker": {
        3: ("disguise-self",),
        5: ("rope-trick",),
        9: ("fear",),
        13: ("greater-invisibility",),
        17: ("seeming",),
    },
}


RANGER_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "hunter": {
        3: {"features_added": ("hunters-lore", "hunter-prey-colossus-slayer")},
        7: {"features_added": ("hunter-multiattack-defense",)},
        11: {"features_added": ("superior-hunters-prey",)},
        15: {"features_added": ("superior-hunters-defense",)},
    },
    "gloom-stalker": {
        3: {
            "features_added": (
                "gloom-stalker-dread-ambusher",
                "gloom-stalker-combat-spells-1",
                "gloom-stalker-umbral-sight",
            ),
        },
        5: {"features_added": ("gloom-stalker-combat-spells-2",)},
        7: {"features_added": ("gloom-stalker-iron-mind",)},
        9: {"features_added": ("gloom-stalker-combat-spells-3",)},
        11: {"features_added": ("gloom-stalker-stalkers-flurry",)},
        13: {"features_added": ("gloom-stalker-combat-spells-4",)},
        15: {"features_added": ("gloom-stalker-shadowy-dodge",)},
        17: {"features_added": ("gloom-stalker-combat-spells-5",)},
    },
    "beastmaster": {
        3: {"features_added": ("beastmaster-primal-companion",)},
        7: {"features_added": ("beastmaster-exceptional-training",)},
        11: {"features_added": ("beastmaster-bestial-fury",)},
        15: {"features_added": ("beastmaster-share-spells",)},
    },
}
