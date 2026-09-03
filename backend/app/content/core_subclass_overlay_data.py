from __future__ import annotations


CORE_SUBCLASS_DELTA_DATA: dict[str, tuple[str, dict[int, dict[str, tuple[str, ...]]]]] = {
    "circle-land": ("druid", {
        3: {"features_added": ("lands-aid", "land-arid-spells")},
        6: {"features_added": ("natural-recovery",)}, 10: {"features_added": ("natures-ward-fire",)},
        14: {"features_added": ("natures-sanctuary",)},
    }),
    "champion": ("fighter", {
        3: {"features_added": ("improved-critical", "remarkable-athlete")},
        7: {"features_added": ("great-weapon-fighting",)}, 10: {"features_added": ("heroic-warrior",)},
        15: {"features_added": ("superior-critical",), "features_removed": ("improved-critical",)},
        18: {"features_added": ("survivor-defy-death", "survivor-heroic-rally")},
    }),
}
