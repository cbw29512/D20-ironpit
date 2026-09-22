from __future__ import annotations

from collections.abc import Callable

from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level7_profile,
    build_seraphine_dawnshield_level8_profile,
    build_seraphine_dawnshield_level9_profile,
    build_seraphine_dawnshield_level10_profile,
    build_seraphine_dawnshield_level11_profile,
    build_seraphine_dawnshield_level12_profile,
    build_seraphine_dawnshield_level13_profile,
    build_seraphine_dawnshield_level14_profile,
    build_seraphine_dawnshield_level15_profile,
    build_seraphine_dawnshield_level16_profile,
    build_seraphine_dawnshield_level17_profile,
    build_seraphine_dawnshield_level18_profile,
)
from app.content.audited_cleric_life_profile import (
    build_seraphine_dawnshield_level3_profile,
    build_seraphine_dawnshield_level4_profile,
    build_seraphine_dawnshield_level5_profile,
    build_seraphine_dawnshield_level6_profile,
)
from app.content.audited_cleric_profile import (
    build_seraphine_dawnshield_level2_profile,
    build_seraphine_dawnshield_profile,
)
from app.domain.character_builds import CharacterBuildProfile

ProfileBuilder = Callable[[], CharacterBuildProfile]

_BUILDERS: tuple[ProfileBuilder, ...] = (
    build_seraphine_dawnshield_profile,
    build_seraphine_dawnshield_level2_profile,
    build_seraphine_dawnshield_level3_profile,
    build_seraphine_dawnshield_level4_profile,
    build_seraphine_dawnshield_level5_profile,
    build_seraphine_dawnshield_level6_profile,
    build_seraphine_dawnshield_level7_profile,
    build_seraphine_dawnshield_level8_profile,
    build_seraphine_dawnshield_level9_profile,
    build_seraphine_dawnshield_level10_profile,
    build_seraphine_dawnshield_level11_profile,
    build_seraphine_dawnshield_level12_profile,
    build_seraphine_dawnshield_level13_profile,
    build_seraphine_dawnshield_level14_profile,
    build_seraphine_dawnshield_level15_profile,
    build_seraphine_dawnshield_level16_profile,
    build_seraphine_dawnshield_level17_profile,
    build_seraphine_dawnshield_level18_profile,
)


def build_seraphine_dawnshield_certified_profile(level: int) -> CharacterBuildProfile:
    if not 1 <= level <= len(_BUILDERS):
        raise ValueError(f"Seraphine certified profile level {level} is unavailable.")
    return _BUILDERS[level - 1]()
