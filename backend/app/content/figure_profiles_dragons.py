from __future__ import annotations

from app.content.figure_profile_schema import FigureProfile, figure_profile

DRAGON_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Black Dragon Wyrmling": figure_profile("reptile", "black-dragon-wyrmling"),
    "Blue Dragon Wyrmling": figure_profile("reptile", "blue-dragon-wyrmling"),
    "Bronze Dragon Wyrmling": figure_profile("reptile", "bronze-dragon-wyrmling"),
    "Dragon Turtle": figure_profile("aquatic-reptile", "dragon-turtle"),
    "Green Dragon Wyrmling": figure_profile("reptile", "green-dragon-wyrmling"),
    "Red Dragon Wyrmling": figure_profile("reptile", "red-dragon-wyrmling"),
    "White Dragon Wyrmling": figure_profile("reptile", "white-dragon-wyrmling"),
    "Young Black Dragon": figure_profile("reptile", "young-black-dragon"),
    "Young Blue Dragon": figure_profile("reptile", "young-blue-dragon"),
    "Young Bronze Dragon": figure_profile("reptile", "young-bronze-dragon"),
    "Young Copper Dragon": figure_profile("reptile", "young-copper-dragon"),
    "Young Green Dragon": figure_profile("reptile", "young-green-dragon"),
    "Young Red Dragon": figure_profile("reptile", "young-red-dragon"),
    "Young White Dragon": figure_profile("reptile", "young-white-dragon"),
}
