from __future__ import annotations

from app.content.figure_profiles import FigureProfile, MONSTER_FIGURE_PROFILES

_NATIVE_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Black Dragon Wyrmling": {"form": "reptile", "detail": "black-dragon-wyrmling"},
    "Blue Dragon Wyrmling": {"form": "reptile", "detail": "blue-dragon-wyrmling"},
    "Green Dragon Wyrmling": {"form": "reptile", "detail": "green-dragon-wyrmling"},
    "Hell Hound": {"form": "quadruped", "detail": "hell-hound"},
    "Red Dragon Wyrmling": {"form": "reptile", "detail": "red-dragon-wyrmling"},
    "White Dragon Wyrmling": {"form": "reptile", "detail": "white-dragon-wyrmling"},
}


def reviewed_monster_figure_profiles() -> dict[str, FigureProfile]:
    overlap = set(MONSTER_FIGURE_PROFILES) & set(_NATIVE_FIGURE_PROFILES)
    if overlap:
        raise ValueError(f"Figure profile names overlap across registries: {sorted(overlap)}")
    return {**MONSTER_FIGURE_PROFILES, **_NATIVE_FIGURE_PROFILES}
