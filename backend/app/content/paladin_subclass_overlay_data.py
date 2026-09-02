from __future__ import annotations


PALADIN_OATH_SPELLS: dict[str, dict[int, tuple[str, ...]]] = {
    "oath-devotion": {
        3: ("protection-from-evil-and-good", "shield-of-faith"),
        5: ("aid", "zone-of-truth"),
        9: ("beacon-of-hope", "dispel-magic"),
        13: ("freedom-of-movement", "guardian-of-faith"),
        17: ("commune", "flame-strike"),
    },
    "oath-vengeance": {
        3: ("bane", "hunters-mark"),
        5: ("hold-person", "misty-step"),
        9: ("haste", "protection-from-energy"),
        13: ("banishment", "dimension-door"),
        17: ("hold-monster", "scrying"),
    },
    "oath-ancients": {
        3: ("ensnaring-strike", "speak-with-animals"),
        5: ("misty-step", "moonbeam"),
        9: ("plant-growth", "protection-from-energy"),
        13: ("ice-storm", "stoneskin"),
        17: ("commune-with-nature", "tree-stride"),
    },
}


PALADIN_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "oath-devotion": {
        3: {"features_added": ("sacred-weapon", "devotion-combat-spells-1")},
        5: {"features_added": ("devotion-combat-spells-2",)},
        7: {"features_added": ("aura-of-devotion",)},
        9: {"features_added": ("devotion-combat-spells-3",)},
        13: {"features_added": ("devotion-combat-spells-4",)},
        15: {"features_added": ("smite-of-protection",)},
        17: {"features_added": ("devotion-combat-spells-5",)},
        20: {"features_added": ("holy-nimbus",)},
    },
    "oath-vengeance": {
        3: {"features_added": ("vow-of-enmity", "vengeance-combat-spells-1")},
        5: {"features_added": ("vengeance-combat-spells-2",)},
        7: {"features_added": ("relentless-avenger",)},
        9: {"features_added": ("vengeance-combat-spells-3",)},
        13: {"features_added": ("vengeance-combat-spells-4",)},
        15: {"features_added": ("soul-of-vengeance",)},
        17: {"features_added": ("vengeance-combat-spells-5",)},
        20: {"features_added": ("avenging-angel",)},
    },
    "oath-ancients": {
        3: {"features_added": ("natures-wrath", "ancients-combat-spells-1")},
        5: {"features_added": ("ancients-combat-spells-2",)},
        7: {"features_added": ("aura-of-warding",)},
        9: {"features_added": ("ancients-combat-spells-3",)},
        13: {"features_added": ("ancients-combat-spells-4",)},
        15: {"features_added": ("undying-sentinel",)},
        17: {"features_added": ("ancients-combat-spells-5",)},
        20: {"features_added": ("elder-champion",)},
    },
}
