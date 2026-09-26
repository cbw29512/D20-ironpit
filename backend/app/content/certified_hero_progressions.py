from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level7_profile,
    build_seraphine_dawnshield_level8_profile,
    build_seraphine_dawnshield_level9_profile,
    build_seraphine_dawnshield_level10_profile,
    build_seraphine_dawnshield_level11_profile,
    build_seraphine_dawnshield_level12_profile,
)
from app.content.audited_cleric_life_profile import (
    build_seraphine_dawnshield_level3_profile, build_seraphine_dawnshield_level4_profile,
    build_seraphine_dawnshield_level5_profile, build_seraphine_dawnshield_level6_profile,
)
from app.content.audited_cleric_profile import build_seraphine_dawnshield_level2_profile, build_seraphine_dawnshield_profile
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.audited_rogue import build_mara_quickstep_level
from app.content.audited_rogue_profile import build_mara_quickstep_profile
from app.content.rogue_progression_profile import (
    build_mara_quickstep_level2_profile, build_mara_quickstep_level3_profile,
    build_mara_quickstep_level4_profile, build_mara_quickstep_level5_profile,
)
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level13_profile, build_mara_quickstep_level14_profile, build_mara_quickstep_level15_profile, build_mara_quickstep_level16_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level17_profile, build_mara_quickstep_level18_profile, build_mara_quickstep_level19_profile, build_mara_quickstep_level20_profile
from app.content.rogue_high_progression_profile import (
    build_mara_quickstep_level9_profile, build_mara_quickstep_level10_profile,
    build_mara_quickstep_level11_profile, build_mara_quickstep_level12_profile,
)
from app.content.rogue_mid_progression_profile import (
    build_mara_quickstep_level6_profile, build_mara_quickstep_level7_profile,
    build_mara_quickstep_level8_profile,
)
from app.content.barbarian_berserker_2014_profile import build_rokhan_stonefury_2014_profile
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level6_profile, build_rokhan_stonefury_level7_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.barbarian_progression_profile import (
    build_rokhan_stonefury_level2_profile, build_rokhan_stonefury_level3_profile,
    build_rokhan_stonefury_level4_profile, build_rokhan_stonefury_level5_profile,
)
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level6_profile, build_karnok_stoneward_level8_profile, build_karnok_stoneward_level12_profile
from app.content.fighter_champion_2014_profile import build_karnok_stoneward_2014_profile
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.fighter_champion_progression_profile import build_karnok_stoneward_level7_profile
from app.content.fighter_level10_profile import build_karnok_stoneward_level10_profile
from app.content.fighter_level11_profile import build_karnok_stoneward_level11_profile
from app.content.fighter_endgame_profile import build_karnok_stoneward_level18_profile
from app.content.fighter_high_level_profile import (
    build_karnok_stoneward_level13_profile, build_karnok_stoneward_level14_profile,
    build_karnok_stoneward_level15_profile, build_karnok_stoneward_level16_profile,
    build_karnok_stoneward_level17_profile,
)
from app.content.fighter_level9_profile import build_karnok_stoneward_level9_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.fighter_progression_profile import (
    build_karnok_stoneward_level2_profile, build_karnok_stoneward_level3_profile,
    build_karnok_stoneward_level4_profile, build_karnok_stoneward_level5_profile,
)
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.rogue_thief_2014_profile import build_mara_quickstep_2014_profile
from app.content.rogue_thief_2014_runtime import build_mara_quickstep_2014
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate
from app.domain.rulesets import RulesetId

ProfileBuilder = Callable[[], CharacterBuildProfile]
ProfileLevelBuilder = Callable[[int], CharacterBuildProfile]
TemplateLevelBuilder = Callable[[int], CombatantTemplate]


@dataclass(frozen=True)
class CertifiedHeroProgression:
    class_id: str
    ruleset: RulesetId
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
        class_id="fighter", ruleset="2024", template_builder=build_karnok_stoneward_level,
        profile_builders=(
            build_karnok_stoneward_profile, build_karnok_stoneward_level2_profile,
            build_karnok_stoneward_level3_profile, build_karnok_stoneward_level4_profile,
            build_karnok_stoneward_level5_profile, build_karnok_stoneward_level6_profile,
            build_karnok_stoneward_level7_profile, build_karnok_stoneward_level8_profile,
            build_karnok_stoneward_level9_profile, build_karnok_stoneward_level10_profile,
            build_karnok_stoneward_level11_profile, build_karnok_stoneward_level12_profile,
            build_karnok_stoneward_level13_profile, build_karnok_stoneward_level14_profile,
            build_karnok_stoneward_level15_profile, build_karnok_stoneward_level16_profile,
            build_karnok_stoneward_level17_profile, build_karnok_stoneward_level18_profile,
        ),
    ),
    CertifiedHeroProgression(
        class_id="fighter", ruleset="2014", template_builder=build_karnok_stoneward_2014,
        profile_level_builder=build_karnok_stoneward_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="barbarian", ruleset="2024", template_builder=build_rokhan_stonefury_level,
        profile_builders=(
            build_rokhan_stonefury_profile, build_rokhan_stonefury_level2_profile,
            build_rokhan_stonefury_level3_profile, build_rokhan_stonefury_level4_profile,
            build_rokhan_stonefury_level5_profile, build_rokhan_stonefury_level6_profile,
            build_rokhan_stonefury_level7_profile,
        ),
    ),
    CertifiedHeroProgression(
        class_id="barbarian", ruleset="2014", template_builder=build_rokhan_stonefury_2014,
        profile_level_builder=build_rokhan_stonefury_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="bard", ruleset="2014", template_builder=build_lyra_silverstring_2014,
        profile_level_builder=build_lyra_silverstring_2014_profile, max_level=2,
    ),
    CertifiedHeroProgression(
        class_id="cleric", ruleset="2024", template_builder=build_seraphine_dawnshield_level,
        profile_builders=(
            build_seraphine_dawnshield_profile, build_seraphine_dawnshield_level2_profile,
            build_seraphine_dawnshield_level3_profile, build_seraphine_dawnshield_level4_profile,
            build_seraphine_dawnshield_level5_profile, build_seraphine_dawnshield_level6_profile,
            build_seraphine_dawnshield_level7_profile, build_seraphine_dawnshield_level8_profile,
            build_seraphine_dawnshield_level9_profile, build_seraphine_dawnshield_level10_profile,
            build_seraphine_dawnshield_level11_profile, build_seraphine_dawnshield_level12_profile,
        ),
    ),
    CertifiedHeroProgression(
        class_id="cleric", ruleset="2014", template_builder=build_seraphine_dawnshield_2014,
        profile_level_builder=build_seraphine_dawnshield_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="rogue", ruleset="2024", template_builder=build_mara_quickstep_level,
        profile_builders=(
            build_mara_quickstep_profile, build_mara_quickstep_level2_profile,
            build_mara_quickstep_level3_profile, build_mara_quickstep_level4_profile,
            build_mara_quickstep_level5_profile, build_mara_quickstep_level6_profile,
            build_mara_quickstep_level7_profile, build_mara_quickstep_level8_profile,
            build_mara_quickstep_level9_profile, build_mara_quickstep_level10_profile,
            build_mara_quickstep_level11_profile, build_mara_quickstep_level12_profile,
            build_mara_quickstep_level13_profile, build_mara_quickstep_level14_profile, build_mara_quickstep_level15_profile, build_mara_quickstep_level16_profile,
            build_mara_quickstep_level17_profile, build_mara_quickstep_level18_profile, build_mara_quickstep_level19_profile, build_mara_quickstep_level20_profile,
        ),
    ),
    CertifiedHeroProgression(
        class_id="rogue", ruleset="2014", template_builder=build_mara_quickstep_2014,
        profile_level_builder=build_mara_quickstep_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="monk", ruleset="2014", template_builder=build_kael_stillwater_2014,
        profile_level_builder=build_kael_stillwater_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="paladin", ruleset="2014", template_builder=build_aurelia_brightshield_2014,
        profile_level_builder=build_aurelia_brightshield_2014_profile, max_level=20,
    ),
)


def iter_certified_progression_levels(
    ruleset: RulesetId | None = None,
) -> list[tuple[CertifiedHeroProgression, int]]:
    return [
        (progression, level)
        for progression in CERTIFIED_HERO_PROGRESSIONS
        if ruleset is None or progression.ruleset == ruleset
        for level in progression.levels
    ]
