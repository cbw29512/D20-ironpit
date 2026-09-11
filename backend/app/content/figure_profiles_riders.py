from app.content.figure_profile_schema import FigureProfile, figure_profile as _p


RIDER_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Ettin": _p("brute", "ettin"),
    "Fire Giant": _p("brute", "fire-giant"),
    "Specter": _p("humanoid", "specter"),
    "Stirge": _p("winged-insect", "stirge"),
}
