from __future__ import annotations

from app.content.barbarian_berserker_2014_profile import build_rokhan_stonefury_2014_profile
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.certified_hero_progression_model import CertifiedHeroProgression
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.druid_land_2014_profile import build_thalen_greenbough_2014_profile
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.fighter_champion_2014_profile import build_karnok_stoneward_2014_profile
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014
from app.content.rogue_thief_2014_profile import build_mara_quickstep_2014_profile
from app.content.rogue_thief_2014_runtime import build_mara_quickstep_2014
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014

CERTIFIED_HERO_PROGRESSIONS_2014: tuple[CertifiedHeroProgression, ...] = (
    CertifiedHeroProgression(
        class_id="fighter", ruleset="2014", template_builder=build_karnok_stoneward_2014,
        profile_level_builder=build_karnok_stoneward_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="barbarian", ruleset="2014", template_builder=build_rokhan_stonefury_2014,
        profile_level_builder=build_rokhan_stonefury_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="bard", ruleset="2014", template_builder=build_lyra_silverstring_2014,
        profile_level_builder=build_lyra_silverstring_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="cleric", ruleset="2014", template_builder=build_seraphine_dawnshield_2014,
        profile_level_builder=build_seraphine_dawnshield_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="druid", ruleset="2014", template_builder=build_thalen_greenbough_2014,
        profile_level_builder=build_thalen_greenbough_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="ranger", ruleset="2014", template_builder=build_rowan_ashtrail_2014,
        profile_level_builder=build_rowan_ashtrail_2014_profile, max_level=20,
    ),
    CertifiedHeroProgression(
        class_id="sorcerer", ruleset="2014", template_builder=build_nyra_emberveil_2014,
        profile_level_builder=build_nyra_emberveil_2014_profile, max_level=2,
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
