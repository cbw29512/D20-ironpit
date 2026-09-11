from __future__ import annotations

from app.content.figure_profile_schema import FigureProfile, figure_profile as _p

NEW_READY_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Animated Rug of Smothering": _p("weapon", "animated-rug"),
    "Bone Devil": _p("humanoid", "bone-devil"),
    "Bulette": _p("quadruped", "bulette"),
    "Chimera": _p("quadruped", "chimera"),
    "Cockatrice": _p("bird", "cockatrice"),
    "Copper Dragon Wyrmling": _p("reptile", "copper-dragon"),
    "Ghast": _p("humanoid", "ghast"),
    "Ghoul": _p("humanoid", "ghoul"),
    "Gold Dragon Wyrmling": _p("reptile", "gold-dragon"),
    "Horned Devil": _p("humanoid", "horned-devil"),
    "Mummy": _p("humanoid", "mummy"),
    "Pirate": _p("humanoid", "pirate"),
    "Pseudodragon": _p("reptile", "pseudodragon"),
    "Seahorse": _p("fish", "seahorse"),
    "Wight": _p("humanoid", "wight"),
    "Winter Wolf": _p("quadruped", "canine"),
    "Wolf": _p("quadruped", "canine"),
    "Worg": _p("quadruped", "canine"),
    "Wyvern": _p("reptile", "wyvern"),
    "Xorn": _p("brute", "xorn"),
    "Young Gold Dragon": _p("reptile", "gold-dragon"),
}

__all__ = ["NEW_READY_FIGURE_PROFILES"]
