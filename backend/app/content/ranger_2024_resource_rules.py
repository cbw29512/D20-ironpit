from __future__ import annotations

from app.content.ranger_combat_levels import RANGER_COMBAT_LEVELS
from app.domain.character_builds import CharacterBuildProfile


def favored_enemy_uses(level: int) -> int:
    try:
        row = RANGER_COMBAT_LEVELS.get(level)
        if row is None:
            raise ValueError("2024 Ranger Favored Enemy covers levels 1 through 20.")
        return row.favored_enemy_uses
    except Exception as exc:
        raise ValueError(f"Failed to resolve 2024 Favored Enemy uses for level {level}.") from exc


def ranger_wisdom_resource_uses(profile: CharacterBuildProfile, minimum_level: int) -> int:
    try:
        if profile.level < minimum_level:
            return 0
        return max(1, profile.final_ability_scores.modifier("wisdom"))
    except Exception as exc:
        raise ValueError(
            f"Failed to resolve 2024 Ranger Wisdom-scaled uses at level {profile.level}."
        ) from exc


def ranger_2024_extra_resources(profile: CharacterBuildProfile) -> dict[str, int]:
    try:
        resolved: dict[str, int] = {}
        tireless = ranger_wisdom_resource_uses(profile, 10)
        if tireless:
            resolved["tireless"] = tireless
        veil = ranger_wisdom_resource_uses(profile, 14)
        if veil:
            resolved["natures-veil"] = veil
        return resolved
    except Exception as exc:
        raise ValueError(f"Failed to resolve extra 2024 Ranger resources at level {profile.level}.") from exc
