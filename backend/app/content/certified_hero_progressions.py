from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_profile import (
    build_seraphine_dawnshield_level3_profile,
    build_seraphine_dawnshield_level4_profile,
)
from app.content.audited_cleric_profile import (
    build_seraphine_dawnshield_level2_profile,
    build_seraphine_dawnshield_profile,
)
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level6_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.barbarian_progression_profile import (
    build_rokhan_stonefury_level2_profile,
    build_rokhan_stonefury_level3_profile,
    build_rokhan_stonefury_level4_profile,
    build_rokhan_stonefury_level5_profile,
)
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level6_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.fighter_progression_profile import (
    build_karnok_stoneward_level2_profile,
    build_karnok_stoneward_level3_profile,
    build_karnok_stoneward_level4_profile,
    build_karnok_stoneward_level5_profile,
)
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate

ProfileBuilder = Callable[[], CharacterBuildProfile]
TemplateLevelBuilder = Callable[[int], CombatantTemplate]


@dataclass(frozen=True)
class CertifiedHeroProgression:
    class_id: str
    template_builder: TemplateLevelBuilder
    profile_builders: tuple[ProfileBuilder, ...]

    @property
    def levels(self) -> range:
        return range(1, len(self.profile_builders) + 1)

    def profile(self, level: int) -> CharacterBuildProfile:
        if level not in self.levels:
            raise ValueError(f"{self.class_id} level {level} is not registered for certification.")
        return self.profile_builders[level - 1]()


CERTIFIED_HERO_PROGRESSIONS: tuple[CertifiedHeroProgression, ...] = (
    CertifiedHeroProgression(
        class_id="fighter",
        template_builder=build_karnok_stoneward_level,
        profile_builders=(
            build_karnok_stoneward_profile,
            build_karnok_stoneward_level2_profile,
            build_karnok_stoneward_level3_profile,
            build_karnok_stoneward_level4_profile,
            build_karnok_stoneward_level5_profile,
            build_karnok_stoneward_level6_profile,
        ),
    ),
    CertifiedHeroProgression(
        class_id="barbarian",
        template_builder=build_rokhan_stonefury_level,
        profile_builders=(
            build_rokhan_stonefury_profile,
            build_rokhan_stonefury_level2_profile,
            build_rokhan_stonefury_level3_profile,
            build_rokhan_stonefury_level4_profile,
            build_rokhan_stonefury_level5_profile,
            build_rokhan_stonefury_level6_profile,
        ),
    ),
    CertifiedHeroProgression(
        class_id="cleric",
        template_builder=build_seraphine_dawnshield_level,
        profile_builders=(
            build_seraphine_dawnshield_profile,
            build_seraphine_dawnshield_level2_profile,
            build_seraphine_dawnshield_level3_profile,
            build_seraphine_dawnshield_level4_profile,
        ),
    ),
)


def iter_certified_progression_levels() -> list[tuple[CertifiedHeroProgression, int]]:
    return [
        (progression, level)
        for progression in CERTIFIED_HERO_PROGRESSIONS
        for level in progression.levels
    ]
