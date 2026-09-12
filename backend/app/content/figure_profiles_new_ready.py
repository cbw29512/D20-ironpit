from __future__ import annotations

from app.content.figure_profile_schema import FigureProfile, figure_profile as _p

NEW_READY_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Animated Rug of Smothering": _p("weapon", "animated-rug"),
    "Assassin": _p("humanoid", "assassin"),
    "Basilisk": _p("reptile", "basilisk"),
    "Bone Devil": _p("humanoid", "bone-devil"),
    "Bulette": _p("quadruped", "bulette"),
    "Chimera": _p("quadruped", "chimera"),
    "Chuul": _p("crab", "chuul"),
    "Cockatrice": _p("bird", "cockatrice"),
    "Copper Dragon Wyrmling": _p("reptile", "copper-dragon"),
    "Elephant": _p("quadruped", "elephant"),
    "Ghast": _p("humanoid", "ghast"),
    "Ghoul": _p("humanoid", "ghoul"),
    "Gladiator": _p("humanoid", "gladiator"),
    "Gold Dragon Wyrmling": _p("reptile", "gold-dragon"),
    "Gorgon": _p("quadruped", "gorgon"),
    "Homunculus": _p("winged", "homunculus"),
    "Horned Devil": _p("humanoid", "horned-devil"),
    "Mammoth": _p("quadruped", "mammoth"),
    "Medusa": _p("humanoid", "medusa"),
    "Mummy": _p("humanoid", "mummy"),
    "Otyugh": _p("brute", "otyugh"),
    "Pirate": _p("humanoid", "pirate"),
    "Pseudodragon": _p("reptile", "pseudodragon"),
    "Seahorse": _p("fish", "seahorse"),
    "Shrieker Fungus": _p("plant", "shrieker-fungus"),
    "Swarm of Ravens": _p("swarm", "ravens"),
    "Wight": _p("humanoid", "wight"),
    "Winter Wolf": _p("quadruped", "canine"),
    "Wolf": _p("quadruped", "canine"),
    "Worg": _p("quadruped", "canine"),
    "Wraith": _p("humanoid", "wraith"),
    "Wyvern": _p("reptile", "wyvern"),
    "Xorn": _p("brute", "xorn"),
    "Young Gold Dragon": _p("reptile", "gold-dragon"),
}

__all__ = ["NEW_READY_FIGURE_PROFILES"]
