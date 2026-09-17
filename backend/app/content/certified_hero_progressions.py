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
from app.content.audited_rogue import build_mara_quickstep_level
from app.content.audited_rogue_profile import build_mara_quickstep_profile
from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level6_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.barbarian_progression_profile import (
    build_rokhan_stonefury_level2_profile,
    build_rokhan_stonefury_level3_profile,
    build_rokhan_stonefury_level4_profile,
    build_rokhan_stonefury_level5_profile,
)
from app.content.fighter_asi_progression_profile import (
    build_karnok_stoneward_level6_profile,
    build_karnok_stoneward_level8_profile,
    build_karnok_stoneward_level12_profile,
)
from app.content.fighter_champion_2014_profile import build_karnok_stoneward_2014_profile
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.fighter_champion_progression_profile import build_karnok_stoneward_level7_profile
from app.content.fighter_level10_profile import build_karnok_stoneward_level10_profile
from app.content.fighter_level11_profile import build_karnok_stoneward_level11_profile
from app.content.fighter_level9_profile import build_karnok_stoneward_level9_profile
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
ProfileLevelBuilder = Callable[[int], CharacterBuildProfile]
TemplateLevelBuilder = Callable[[int], CombatantTemplate]


@dataclass(frozen=True)
class CertifiedHeroProgression:
    class_id: str
    template_builder: TemplateLevelBuilder
    profile_builders: tuple[ProfileBuilder, ...] = ()
    profile_level_builder: ProfileLevelBuilder | None = None
    max_level: int | None = None

    @property
    def levels(self) -> range:
        count = self.max_level if self.max_level is not None else len(self.profile_builders)
        return range(1, count + 1)

    def profile(self, level: int) -> CharacterBuildProfile:
        if level not in self.levels:
            raise ValueError(f"{self.class_id} level {level} is not registered for certification.")
        if self.profile_level_builder is not None:
            return self.profile_level_builder(level)
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
            build_karnok_stoneward_level7_profile,
            build_karnok_stoneward_level8_profile,
            build_karnok_stoneward_level9_profile,
            build_karnok_stoneward_level10_profile,
            build_karnok_stoneward_level11_profile,
            build_karnok_stoneward_level12_profile,
        ),
    ),
    CertifiedHeroProgression(
        class_id="fighter",
        template_builder=build_karnok_stoneward_2014,
        profile_level_builder=build_karnok_stoneward_2014_profile,
        max_level=20,
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
    CertifiedHeroProgression(
        class_id="rogue",
        template_builder=build_mara_quickstep_level,
        profile_builders=(build_mara_quickstep_profile,),
    ),
)


def iter_certified_progression_levels() -> list[tuple[CertifiedHeroProgression, int]]:
    return [
        (progression, level)
        for progression in CERTIFIED_HERO_PROGRESSIONS
        for level in progression.levels
    ]
