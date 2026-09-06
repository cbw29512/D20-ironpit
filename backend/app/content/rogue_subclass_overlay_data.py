from __future__ import annotations


ROGUE_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "thief": {
        3: {
            "arena_ignored": ("thief-fast-hands", "thief-second-story-work"),
        },
        9: {"features_added": ("thief-supreme-sneak",)},
        13: {"features_added": ("thief-use-magic-device",)},
        17: {"features_added": ("thiefs-reflexes",)},
    },
    "assassin": {
        3: {
            "features_added": ("assassin-assassinate",),
            "arena_ignored": ("assassin-tools",),
        },
        9: {"features_added": ("assassin-infiltration-expertise",)},
        13: {"features_added": ("assassin-envenom-weapons",)},
        17: {"features_added": ("assassin-death-strike",)},
    },
    "arcane-trickster": {
        3: {"features_added": ("arcane-trickster-spellcasting", "mage-hand-legerdemain")},
        9: {"features_added": ("arcane-trickster-magical-ambush",)},
        13: {"features_added": ("arcane-trickster-versatile-trickster",)},
        17: {"features_added": ("arcane-trickster-spell-thief",)},
    },
}
