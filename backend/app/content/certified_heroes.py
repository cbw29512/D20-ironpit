from __future__ import annotations

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.certified_hero_progressions import iter_certified_progression_levels
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.fighter_2014 import build_certified_2014_fighter_levels
from app.content.hero_progressions import CANONICAL_BUILD_ID
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate

HeroBuildKey = tuple[str, int, str]
HeroCatalogReady = tuple[str, str]


def _validated(
    template: CombatantTemplate,
    profile: CharacterBuildProfile,
) -> tuple[HeroBuildKey, CombatantTemplate]:
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, template)
    combat_profile = build_pregen_combat_profiles().get(template.id)
    if combat_profile is None:
        raise ValueError(f"Certified hero {template.id} lacks a combat fingerprint.")
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    template = complete_unarmed_opportunity_profiles([template])[0]
    return (profile.class_id, profile.level, CANONICAL_BUILD_ID), template


def _validated_2014(template: CombatantTemplate) -> tuple[HeroBuildKey, CombatantTemplate]:
    if template.ruleset != "2014" or template.archetype != "Fighter":
        raise ValueError(f"2014 test hero {template.id} crossed its ruleset/class boundary.")
    if template.level not in range(1, 11):
        raise ValueError(f"2014 test hero {template.id} is outside the certified level 1-10 lane.")
    if template.weapon_masteries:
        raise ValueError(f"2014 test hero {template.id} illegally received 2024 Weapon Mastery.")
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    if any(attack.weapon.mastery_property is not None for attack in attacks):
        raise ValueError(f"2014 test hero {template.id} exported a 2024 weapon mastery property.")
    template = complete_unarmed_opportunity_profiles([template])[0]
    return ("fighter", template.level, "canonical-2014"), template


def build_certified_hero_entries() -> list[tuple[HeroBuildKey, CombatantTemplate]]:
    """Validate all certified 2024 progressions plus the isolated 2014 test lane."""
    entries = [
        _validated(progression.template_builder(level), progression.profile(level))
        for progression, level in iter_certified_progression_levels()
    ]
    entries.extend(_validated_2014(template) for template in build_certified_2014_fighter_levels())
    return entries


def build_certified_hero_registry() -> dict[HeroBuildKey, HeroCatalogReady]:
    return {key: (template.name, template.id) for key, template in build_certified_hero_entries()}


def build_certified_hero_templates() -> list[CombatantTemplate]:
    return [template for _, template in build_certified_hero_entries()]
