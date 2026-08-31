from __future__ import annotations

from collections.abc import Callable

from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.audited_fighter import build_karnok_stoneward
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
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
    build_id: str,
) -> tuple[HeroBuildKey, CombatantTemplate]:
    template = template_builder()
    profile = profile_builder()
    assert_character_build_raw_ready(profile, template)
    combat_profile = build_pregen_combat_profiles().get(template.id)
    if combat_profile is None:
        raise ValueError(f"Certified hero {template.id} lacks a combat fingerprint.")
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    template = complete_unarmed_opportunity_profiles([template])[0]
    return (profile.class_id, profile.level, build_id), template


def build_certified_hero_entries() -> list[tuple[HeroBuildKey, CombatantTemplate]]:
    """Return only builds that pass legality, combat-stat, and level-scaling audits."""
    return [
        _validated(build_karnok_stoneward, build_karnok_stoneward_profile, "great-weapon"),
        _validated(build_rokhan_stonefury, build_rokhan_stonefury_profile, "great-weapon"),
    ]


def build_certified_hero_registry() -> dict[HeroBuildKey, HeroCatalogReady]:
    return {key: (template.name, template.id) for key, template in build_certified_hero_entries()}


def build_certified_hero_templates() -> list[CombatantTemplate]:
    return [template for _, template in build_certified_hero_entries()]
