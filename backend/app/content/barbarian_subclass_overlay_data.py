from __future__ import annotations


BARBARIAN_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "path-berserker": {
        3: {"features_added": ("frenzy",)},
        6: {"features_added": ("mindless-rage",)},
        10: {"features_added": ("retaliation",)},
        14: {"features_added": ("intimidating-presence",)},
    },
    "path-wild-heart": {
        3: {
            "features_added": ("wild-heart-rage-of-the-wilds",),
            "arena_ignored": ("wild-heart-animal-speaker",),
        },
        6: {"features_added": ("wild-heart-aspect-of-the-wilds",)},
        10: {"arena_ignored": ("wild-heart-nature-speaker",)},
        14: {"features_added": ("wild-heart-power-of-the-wilds",)},
    },
    "path-zealot": {
        3: {"features_added": ("zealot-divine-fury", "zealot-warrior-of-the-gods")},
        6: {"features_added": ("zealot-fanatical-focus",)},
        10: {"features_added": ("zealot-zealous-presence",)},
        14: {"features_added": ("zealot-rage-of-the-gods",)},
    },
}
