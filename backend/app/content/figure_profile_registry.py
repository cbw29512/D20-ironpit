from __future__ import annotations

from app.content.figure_profiles import FigureProfile, MONSTER_FIGURE_PROFILES

_NATIVE_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Green Dragon Wyrmling": {"form": "reptile", "detail": "green-dragon-wyrmling"},
}


def reviewed_monster_figure_profiles() -> dict[str, FigureProfile]:
    overlap = set(MONSTER_FIGURE_PROFILES) & set(_NATIVE_FIGURE_PROFILES)
    if overlap:
        raise ValueError(f"Figure profile names overlap across registries: {sorted(overlap)}")
    return {**MONSTER_FIGURE_PROFILES, **_NATIVE_FIGURE_PROFILES}
