from __future__ import annotations


DRUID_SUBCLASS_SPELLS: dict[str, dict[int, tuple[str, ...]]] = {
    "circle-land": {
        3: ("blur", "burning-hands", "fire-bolt"),
        5: ("fireball",), 7: ("blight",), 9: ("wall-of-stone",),
    },
    "circle-moon": {
        3: ("cure-wounds", "moonbeam", "starry-wisp"),
        5: ("conjure-animals",), 7: ("fount-of-moonlight",), 9: ("mass-cure-wounds",),
    },
    "circle-sea": {
        3: ("fog-cloud", "gust-of-wind", "ray-of-frost", "shatter", "thunderwave"),
        5: ("lightning-bolt", "water-breathing"),
        7: ("control-water", "ice-storm"),
        9: ("conjure-elemental", "hold-monster"),
    },
}


DRUID_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "circle-land": {
        3: {"features_added": ("lands-aid", "land-arid-spells")},
        6: {"features_added": ("natural-recovery",)},
        10: {"features_added": ("natures-ward-fire",)},
        14: {"features_added": ("natures-sanctuary",)},
    },
    "circle-moon": {
        3: {"features_added": ("circle-forms", "circle-moon-spells")},
        6: {"features_added": ("improved-circle-forms",)},
        10: {"features_added": ("moonlight-step",)},
        14: {"features_added": ("lunar-form",)},
    },
    "circle-sea": {
        3: {"features_added": ("wrath-of-the-sea", "circle-sea-spells")},
        6: {"features_added": ("aquatic-affinity",)},
        10: {"features_added": ("stormborn",)},
        14: {"features_added": ("oceanic-gift",)},
    },
}
