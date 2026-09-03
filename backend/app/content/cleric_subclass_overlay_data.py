from __future__ import annotations


CLERIC_DOMAIN_SPELLS: dict[str, dict[int, tuple[str, ...]]] = {
    "life-domain": {
        3: ("aid", "bless", "cure-wounds", "lesser-restoration"),
        5: ("mass-healing-word", "revivify"),
        7: ("aura-of-life", "death-ward"),
        9: ("greater-restoration", "mass-cure-wounds"),
    },
    "light-domain": {
        3: ("burning-hands", "faerie-fire", "scorching-ray", "see-invisibility"),
        5: ("daylight", "fireball"),
        7: ("arcane-eye", "wall-of-fire"),
        9: ("flame-strike", "scrying"),
    },
    "war-domain": {
        3: ("guiding-bolt", "magic-weapon", "shield-of-faith", "spiritual-weapon"),
        5: ("crusaders-mantle", "spirit-guardians"),
        7: ("fire-shield", "freedom-of-movement"),
        9: ("hold-monster", "steel-wind-strike"),
    },
}


CLERIC_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "life-domain": {
        3: {"features_added": ("disciple-of-life", "preserve-life")},
        6: {"features_added": ("blessed-healer",)},
        17: {"features_added": ("supreme-healing",)},
    },
    "light-domain": {
        3: {"features_added": ("warding-flare", "radiance-of-the-dawn")},
        6: {"features_added": ("improved-warding-flare",)},
        17: {"features_added": ("corona-of-light",)},
    },
    "war-domain": {
        3: {"features_added": ("war-priest", "guided-strike")},
        6: {"features_added": ("war-gods-blessing",)},
        17: {"features_added": ("avatar-of-battle",)},
    },
}
