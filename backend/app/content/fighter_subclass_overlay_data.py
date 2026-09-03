from __future__ import annotations


FIGHTER_SUBCLASS_DELTA_DATA: dict[str, dict[int, dict[str, tuple[str, ...]]]] = {
    "champion": {
        3: {"features_added": ("improved-critical", "remarkable-athlete")},
        7: {"features_added": ("great-weapon-fighting",)},
        10: {"features_added": ("heroic-warrior",)},
        15: {"features_added": ("superior-critical",), "features_removed": ("improved-critical",)},
        18: {"features_added": ("survivor-defy-death", "survivor-heroic-rally")},
    },
    "battle-master": {
        3: {
            "features_added": ("battle-master-combat-superiority",),
            "arena_ignored": ("battle-master-student-of-war",),
        },
        7: {"features_added": ("battle-master-know-your-enemy",)},
        10: {"features_added": ("battle-master-improved-combat-superiority",)},
        15: {"features_added": ("battle-master-relentless",)},
        18: {"features_added": ("battle-master-ultimate-combat-superiority",)},
    },
    "eldritch-knight": {
        3: {"features_added": ("eldritch-knight-spellcasting", "eldritch-knight-war-bond")},
        7: {"features_added": ("eldritch-knight-war-magic",)},
        10: {"features_added": ("eldritch-knight-eldritch-strike",)},
        15: {"features_added": ("eldritch-knight-arcane-charge",)},
        18: {"features_added": ("eldritch-knight-improved-war-magic",)},
    },
    "psi-warrior": {
        3: {"features_added": ("psi-warrior-psionic-power",)},
        7: {"features_added": ("psi-warrior-telekinetic-adept",)},
        10: {"features_added": ("psi-warrior-guarded-mind",)},
        15: {"features_added": ("psi-warrior-bulwark-of-force",)},
        18: {"features_added": ("psi-warrior-telekinetic-master",)},
    },
}
