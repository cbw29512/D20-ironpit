from __future__ import annotations


MONK_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "warrior-open-hand": {
        3: {"features_added": ("open-hand-technique",)},
        6: {"features_added": ("wholeness-of-body",)},
        11: {"features_added": ("fleet-step",)},
        17: {"features_added": ("quivering-palm",)},
    },
    "warrior-shadow": {
        3: {"features_added": ("shadow-arts",)},
        6: {"features_added": ("shadow-step",)},
        11: {"features_added": ("improved-shadow-step",)},
        17: {"features_added": ("cloak-of-shadows",)},
    },
    "warrior-elements": {
        3: {
            "features_added": ("elemental-attunement",),
            "arena_ignored": ("manipulate-elements",),
        },
        6: {"features_added": ("elemental-burst",)},
        11: {"features_added": ("stride-of-the-elements",)},
        17: {"features_added": ("elemental-epitome",)},
    },
}
