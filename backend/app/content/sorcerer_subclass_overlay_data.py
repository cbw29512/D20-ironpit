from __future__ import annotations


SORCERER_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "draconic-sorcery": {
        3: {"features_added": ("draconic-resilience", "draconic-spells")},
        6: {"features_added": ("elemental-affinity-fire",)},
        14: {"features_added": ("dragon-wings",)},
        18: {"features_added": ("dragon-companion",)},
    },
    "aberrant-sorcery": {
        3: {"features_added": ("psionic-spells", "telepathic-speech")},
        6: {"features_added": ("psionic-sorcery", "psychic-defenses")},
        14: {"features_added": ("revelation-in-flesh",)},
        18: {"features_added": ("warping-implosion",)},
    },
    "clockwork-sorcery": {
        3: {"features_added": ("clockwork-spells", "restore-balance")},
        6: {"features_added": ("bastion-of-law",)},
        14: {"features_added": ("trance-of-order",)},
        18: {"features_added": ("clockwork-cavalcade",)},
    },
}
