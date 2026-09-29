from __future__ import annotations

from app.content.audited_bard import build_lyra_silverstring_level
from app.content.audited_bard_profile_levels import (
    build_lyra_silverstring_level1_profile,
    build_lyra_silverstring_level2_profile,
    build_lyra_silverstring_level3_profile,
    build_lyra_silverstring_level4_profile,
    build_lyra_silverstring_level5_profile,
    build_lyra_silverstring_level6_profile,
    build_lyra_silverstring_level7_profile,
    build_lyra_silverstring_level8_profile,
    build_lyra_silverstring_level9_profile,
    build_lyra_silverstring_level10_profile,
    build_lyra_silverstring_level11_profile,
    build_lyra_silverstring_level12_profile,
    build_lyra_silverstring_level13_profile,
    build_lyra_silverstring_level14_profile,
    build_lyra_silverstring_level15_profile,
    build_lyra_silverstring_level16_profile,
    build_lyra_silverstring_level17_profile,
    build_lyra_silverstring_level18_profile,
    build_lyra_silverstring_level19_profile,
    build_lyra_silverstring_level20_profile,
)
from app.content.certified_hero_progression_model import CertifiedHeroProgression


CERTIFIED_BARD_2024 = CertifiedHeroProgression(
    class_id="bard",
    ruleset="2024",
    template_builder=build_lyra_silverstring_level,
    profile_builders=(
        build_lyra_silverstring_level1_profile,
        build_lyra_silverstring_level2_profile,
        build_lyra_silverstring_level3_profile,
        build_lyra_silverstring_level4_profile,
        build_lyra_silverstring_level5_profile,
        build_lyra_silverstring_level6_profile,
        build_lyra_silverstring_level7_profile,
        build_lyra_silverstring_level8_profile,
        build_lyra_silverstring_level9_profile,
        build_lyra_silverstring_level10_profile,
        build_lyra_silverstring_level11_profile,
        build_lyra_silverstring_level12_profile,
        build_lyra_silverstring_level13_profile,
        build_lyra_silverstring_level14_profile,
        build_lyra_silverstring_level15_profile,
        build_lyra_silverstring_level16_profile,
        build_lyra_silverstring_level17_profile,
        build_lyra_silverstring_level18_profile,
        build_lyra_silverstring_level19_profile,
        build_lyra_silverstring_level20_profile,
    ),
)
