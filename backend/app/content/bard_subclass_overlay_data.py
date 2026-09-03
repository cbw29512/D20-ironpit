from __future__ import annotations


BARD_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "college-lore": {
        3: {"features_added": ("cutting-words",), "arena_ignored": ("lore-bonus-proficiencies",)},
        6: {"features_added": ("magical-discoveries",)},
        14: {"features_added": ("peerless-skill",)},
    },
    "college-valor": {
        3: {"features_added": ("combat-inspiration", "valor-martial-training")},
        6: {"features_added": ("valor-extra-attack",)},
        14: {"features_added": ("battle-magic",)},
    },
    "college-glamour": {
        3: {"features_added": ("beguiling-magic", "mantle-of-inspiration")},
        6: {"features_added": ("mantle-of-majesty",)},
        14: {"features_added": ("unbreakable-majesty",)},
    },
}
