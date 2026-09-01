from __future__ import annotations

from collections.abc import Callable

from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.audited_cleric import (
    build_seraphine_dawnshield,
    build_seraphine_dawnshield_level_three,
    build_seraphine_dawnshield_level_two,
)
from app.content.audited_cleric_life_profile import build_seraphine_dawnshield_level3_profile
from app.content.audited_cleric_profile import build_seraphine_dawnshield_level2_profile, build_seraphine_dawnshield_profile
from app.content.audited_fighter import build_karnok_stoneward
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.fighter_progression_profile import (
    build_karnok_stoneward_level2_profile,
    build_karnok_stoneward_level3_profile,
    build_karnok_stoneward_level4_profile,
    build_karnok_stoneward_level5_profile,
)
from app.content.hero_progressions import CANONICAL_BUILD_ID
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate

HeroBuildKey = tuple[str, int, str]
HeroCatalogReady = tuple[str, str]


def _validated(
    template_builder: Callable[[], CombatantTemplate],
    profile_builder: Callable[[], CharacterBuildProfile],
) -> tuple[HeroBuildKey, CombatantTemplate]:
    template = template_builder()
    profile = profile_builder()
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, template)
    combat_profile = build_pregen_combat_profiles().get(template.id)
    if combat_profile is None:
        raise ValueError(f"Certified hero {template.id} lacks a combat fingerprint.")
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    template = complete_unarmed_opportunity_profiles([template])[0]
    return (profile.class_id, profile.level, CANONICAL_BUILD_ID), template


def build_certified_hero_entries() -> list[tuple[HeroBuildKey, CombatantTemplate]]:
    """Return only canonical hero levels that pass every RAW certification gate."""
    return [
        _validated(build_karnok_stoneward, build_karnok_stoneward_profile),
        _validated(lambda: build_karnok_stoneward_level(2), build_karnok_stoneward_level2_profile),
        _validated(lambda: build_karnok_stoneward_level(3), build_karnok_stoneward_level3_profile),
        _validated(lambda: build_karnok_stoneward_level(4), build_karnok_stoneward_level4_profile),
        _validated(lambda: build_karnok_stoneward_level(5), build_karnok_stoneward_level5_profile),
        _validated(build_rokhan_stonefury, build_rokhan_stonefury_profile),
        _validated(build_seraphine_dawnshield, build_seraphine_dawnshield_profile),
        _validated(build_seraphine_dawnshield_level_two, build_seraphine_dawnshield_level2_profile),
        _validated(build_seraphine_dawnshield_level_three, build_seraphine_dawnshield_level3_profile),
    ]


def build_certified_hero_registry() -> dict[HeroBuildKey, HeroCatalogReady]:
    return {key: (template.name, template.id) for key, template in build_certified_hero_entries()}


def build_certified_hero_templates() -> list[CombatantTemplate]:
    return [template for _, template in build_certified_hero_entries()]
