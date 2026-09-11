from app.content.figure_profile_schema import FigureProfile, figure_profile as _p


RIDER_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Azer Sentinel": _p("humanoid", "azer-sentinel"),
    "Ettin": _p("brute", "ettin"),
    "Fire Giant": _p("brute", "fire-giant"),
    "Hezrou": _p("brute", "hezrou"),
    "Hobgoblin Captain": _p("humanoid", "hobgoblin-captain"),
    "Specter": _p("humanoid", "specter"),
    "Stirge": _p("winged-insect", "stirge"),
}
