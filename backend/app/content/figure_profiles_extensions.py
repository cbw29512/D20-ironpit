from __future__ import annotations

from app.content.figure_profiles_forced_movement import FORCED_MOVEMENT_FIGURE_PROFILES
from app.content.figure_profiles_recharge import RECHARGE_FIGURE_PROFILES
from app.content.figure_profiles_undead import UNDEAD_FIGURE_PROFILES

FIGURE_PROFILE_EXTENSIONS = {
    **UNDEAD_FIGURE_PROFILES,
    **RECHARGE_FIGURE_PROFILES,
    **FORCED_MOVEMENT_FIGURE_PROFILES,
    "Ettin": {"form": "brute", "detail": "ettin"},
    "Fire Giant": {"form": "brute", "detail": "fire-giant"},
}
