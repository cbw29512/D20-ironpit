from __future__ import annotations


WIZARD_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "evoker": {
        3: {"features_added": ("potent-cantrip", "evocation-savant")},
        6: {"features_added": ("sculpt-spells",)},
        10: {"features_added": ("empowered-evocation",)},
        14: {"features_added": ("overchannel",)},
    },
    "illusionist": {
        3: {"features_added": ("illusion-savant", "improved-illusions")},
        6: {"features_added": ("phantasmal-creatures",)},
        10: {"features_added": ("illusory-self",)},
        14: {"features_added": ("illusory-reality",)},
    },
    "abjurer": {
        3: {"features_added": ("abjuration-savant", "arcane-ward")},
        6: {"features_added": ("projected-ward",)},
        10: {"features_added": ("spell-breaker",)},
        14: {"features_added": ("spell-resistance",)},
    },
}
