from __future__ import annotations

from app.content.figure_profile_schema import FigureProfile, figure_profile as _p

NEW_READY_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Animated Rug of Smothering": _p("weapon", "animated-rug"),
    "Bulette": _p("quadruped", "bulette"),
    "Horned Devil": _p("humanoid", "horned-devil"),
    "Mummy": _p("humanoid", "mummy"),
    "Pirate": _p("humanoid", "pirate"),
    "Pseudodragon": _p("reptile", "pseudodragon"),
    "Wight": _p("humanoid", "wight"),
    "Winter Wolf": _p("quadruped", "canine"),
    "Wolf": _p("quadruped", "canine"),
    "Worg": _p("quadruped", "canine"),
    "Wyvern": _p("reptile", "wyvern"),
    "Xorn": _p("brute", "xorn"),
}

__all__ = ["NEW_READY_FIGURE_PROFILES"]