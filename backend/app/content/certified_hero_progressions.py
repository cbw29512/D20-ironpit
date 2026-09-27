from __future__ import annotations

from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level7_profile, build_seraphine_dawnshield_level8_profile,
    build_seraphine_dawnshield_level9_profile, build_seraphine_dawnshield_level10_profile,
    build_seraphine_dawnshield_level11_profile, build_seraphine_dawnshield_level12_profile,
)
from app.content.audited_cleric_life_profile import (
    build_seraphine_dawnshield_level3_profile, build_seraphine_dawnshield_level4_profile,
    build_seraphine_dawnshield_level5_profile, build_seraphine_dawnshield_level6_profile,
)
from app.content.audited_cleric_profile import build_seraphine_dawnshield_level2_profile, build_seraphine_dawnshield_profile
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.audited_rogue import build_mara_quickstep_level
from app.content.audited_rogue_profile import build_mara_quickstep_profile
from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level6_profile, build_rokhan_stonefury_level7_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.barbarian_progression_profile import (
    build_rokhan_stonefury_level2_profile, build_rokhan_stonefury_level3_profile,
    build_rokhan_stonefury_level4_profile, build_rokhan_stonefury_level5_profile,
)
from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.certified_hero_progressions_2014 import CERTIFIED_HERO_PROGRESSIONS_2014
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level6_profile, build_karnok_stoneward_level8_profile, build_karnok_stoneward_level12_profile
from app.content.fighter_champion_progression_profile import build_karnok_stoneward_level7_profile
from app.content.fighter_endgame_profile import build_karnok_stoneward_level18_profile
from app.content.fighter_high_level_profile import (
    build_karnok_stoneward_level13_profile, build_karnok_stoneward_level14_profile,
    build_karnok_stoneward_level15_profile, build_karnok_stoneward_level16_profile,
    build_karnok_stoneward_level17_profile,
)
from app.content.fighter_level10_profile import build_karnok_stoneward_level10_profile
from app.content.fighter_level11_profile import build_karnok_stoneward_level11_profile
from app.content.fighter_level9_profile import build_karnok_stoneward_level9_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.fighter_progression_profile import (
    build_karnok_stoneward_level2_profile, build_karnok_stoneward_level3_profile,
    build_karnok_stoneward_level4_profile, build_karnok_stoneward_level5_profile,
)
from app.content.rogue_endgame_progression_profile import (
    build_mara_quickstep_level13_profile, build_mara_quickstep_level14_profile,
    build_mara_quickstep_level15_profile, build_mara_quickstep_level16_profile,
)
from app.content.rogue_final_progression_profile import (
    build_mara_quickstep_level17_profile, build_mara_quickstep_level18_profile,
    build_mara_quickstep_level19_profile, build_mara_quickstep_level20_profile,
)
from app.content.rogue_high_progression_profile import (
    build_mara_quickstep_level9_profile, build_mara_quickstep_level10_profile,
    build_mara_quickstep_level11_profile, build_mara_quickstep_level12_profile,
)
from app.content.rogue_mid_progression_profile import (
    build_mara_quickstep_level6_profile, build_mara_quickstep_level7_profile,
    build_mara_quickstep_level8_profile,
)
from app.content.rogue_progression_profile import (
    build_mara_quickstep_level2_profile, build_mara_quickstep_level3_profile,
    build_mara_quickstep_level4_profile, build_mara_quickstep_level5_profile,
)
from app.domain.rulesets import RulesetId

CERTIFIED_HERO_PROGRESSIONS_2024: tuple[CertifiedHeroProgression, ...] = (
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
        class_id="barbarian", ruleset="2024", template_builder=build_rokhan_stonefury_level,
        profile_builders=(
            build_rokhan_stonefury_profile, build_rokhan_stonefury_level2_profile,
            build_rokhan_stonefury_level3_profile, build_rokhan_stonefury_level4_profile,
            build_rokhan_stonefury_level5_profile, build_rokhan_stonefury_level6_profile,
            build_rokhan_stonefury_level7_profile,
        ),
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
        class_id="rogue", ruleset="2024", template_builder=build_mara_quickstep_level,
        profile_builders=(
            build_mara_quickstep_profile, build_mara_quickstep_level2_profile,
            build_mara_quickstep_level3_profile, build_mara_quickstep_level4_profile,
            build_mara_quickstep_level5_profile, build_mara_quickstep_level6_profile,
            build_mara_quickstep_level7_profile, build_mara_quickstep_level8_profile,
            build_mara_quickstep_level9_profile, build_mara_quickstep_level10_profile,
            build_mara_quickstep_level11_profile, build_mara_quickstep_level12_profile,
            build_mara_quickstep_level13_profile, build_mara_quickstep_level14_profile,
            build_mara_quickstep_level15_profile, build_mara_quickstep_level16_profile,
            build_mara_quickstep_level17_profile, build_mara_quickstep_level18_profile,
            build_mara_quickstep_level19_profile, build_mara_quickstep_level20_profile,
        ),
    ),
)

CERTIFIED_HERO_PROGRESSIONS = (*CERTIFIED_HERO_PROGRESSIONS_2024, *CERTIFIED_HERO_PROGRESSIONS_2014)


def iter_certified_progression_levels(
    ruleset: RulesetId | None = None,
) -> list[tuple[CertifiedHeroProgression, int]]:
    return [
        (progression, level)
        for progression in CERTIFIED_HERO_PROGRESSIONS
        if ruleset is None or progression.ruleset == ruleset
        for level in progression.levels
    ]
