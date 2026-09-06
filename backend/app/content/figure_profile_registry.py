from __future__ import annotations

from app.content.figure_profiles import FigureProfile, MONSTER_FIGURE_PROFILES

_NATIVE_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Ape": {"form": "primate", "detail": "ape"},
    "Azer Sentinel": {"form": "humanoid", "detail": "azer-sentinel"},
    "Black Dragon Wyrmling": {"form": "reptile", "detail": "black-dragon-wyrmling"},
    "Blue Dragon Wyrmling": {"form": "reptile", "detail": "blue-dragon-wyrmling"},
    "Bugbear Warrior": {"form": "humanoid", "detail": "bugbear-warrior"},
    "Green Dragon Wyrmling": {"form": "reptile", "detail": "green-dragon-wyrmling"},
    "Hell Hound": {"form": "quadruped", "detail": "hell-hound"},
    "Hezrou": {"form": "brute", "detail": "hezrou"},
    "Hill Giant": {"form": "brute", "detail": "hill-giant"},
    "Hobgoblin Captain": {"form": "humanoid", "detail": "hobgoblin-captain"},
    "Lion": {"form": "quadruped", "detail": "lion"},
    "Magmin": {"form": "humanoid", "detail": "magmin"},
    "Merrow": {"form": "brute", "detail": "merrow"},
    "Mimic": {"form": "blob", "detail": "mimic"},
    "Red Dragon Wyrmling": {"form": "reptile", "detail": "red-dragon-wyrmling"},
    "Satyr": {"form": "humanoid", "detail": "satyr"},
    "Specter": {"form": "humanoid", "detail": "specter"},
    "Troll Limb": {"form": "brute", "detail": "troll-limb"},
    "Werebear": {"form": "humanoid", "detail": "werebear-hybrid"},
    "Wereboar": {"form": "humanoid", "detail": "wereboar-hybrid"},
    "Wererat": {"form": "humanoid", "detail": "wererat-hybrid"},
    "Weretiger": {"form": "humanoid", "detail": "weretiger-hybrid"},
    "Werewolf": {"form": "humanoid", "detail": "werewolf-hybrid"},
    "White Dragon Wyrmling": {"form": "reptile", "detail": "white-dragon-wyrmling"},
    "Winter Wolf": {"form": "quadruped", "detail": "winter-wolf"},
    "Wraith": {"form": "humanoid", "detail": "wraith"},
    "Young Black Dragon": {"form": "reptile", "detail": "young-black-dragon"},
    "Young Blue Dragon": {"form": "reptile", "detail": "young-blue-dragon"},
    "Young Green Dragon": {"form": "reptile", "detail": "young-green-dragon"},
    "Young Red Dragon": {"form": "reptile", "detail": "young-red-dragon"},
    "Young White Dragon": {"form": "reptile", "detail": "young-white-dragon"},
}


def reviewed_monster_figure_profiles() -> dict[str, FigureProfile]:
    overlap = set(MONSTER_FIGURE_PROFILES) & set(_NATIVE_FIGURE_PROFILES)
    if overlap:
        raise ValueError(f"Figure profile names overlap across registries: {sorted(overlap)}")
    return {**MONSTER_FIGURE_PROFILES, **_NATIVE_FIGURE_PROFILES}
