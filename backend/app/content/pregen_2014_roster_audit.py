from __future__ import annotations

import logging
from dataclasses import dataclass

from app.content.all_pregen_combat_profiles import build_all_pregen_combat_profiles
from app.content.bard_2014_spell_package import additional_lore_magical_secrets_2014
from app.content.build_audit import audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy, combat_feature_audits
from app.content.canonical_spell_policy import CASTER_CLASS_IDS, canonical_spell_package
from app.content.certified_hero_progressions import iter_certified_progression_levels
from app.content.character_resource_audit import audit_character_resources
from app.content.class_spell_progression import CASTING_ABILITIES
from app.content.grapple_escape_skill_bonuses import complete_template_grapple_escape_skills
from app.content.pregen_combat_audit import audit_pregen_combat_stats
from app.domain.character_builds import CharacterBuildProfile
from app.domain.class_loadouts import CanonicalSpellChoice, ClassSpellPackage
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_NONBLOCKING_SPELL_TAGS = frozenset({"arena-out-of-scope", "arena-unavailable-summon"})
_UNSUPPORTED_SPELL_TAGS = frozenset({"fail-closed", "unbound", "engine-missing"})
EXPECTED_2014_SNAPSHOTS = 240


@dataclass(frozen=True)
class Pregen2014SnapshotAudit:
    class_id: str
    hero_name: str
    level: int
    template_id: str
    checked: bool
    passed: bool
    unsupported_mechanics: tuple[str, ...]


def runtime_binding_ids(template: CombatantTemplate) -> set[str]:
    """Collect declared runtime action/grant IDs without inventing bindings."""
    try:
        ids: set[str] = set()
        for value in template.__dict__.values():
            if not isinstance(value, list):
                continue
            for item in value:
                for attr in ("id", "source_id"):
                    found = getattr(item, attr, None)
                    if isinstance(found, str) and found:
                        ids.add(found)
        return ids
    except Exception:
        logger.exception("Failed to collect runtime binding IDs for %s.", template.id)
        raise


def _policy_issues(profile: CharacterBuildProfile) -> list[str]:
    try:
        assert_canonical_profile_policy(profile)
        return []
    except ValueError as exc:
        return [f"canonical-policy:{exc}"]


def _spell_choices(profile: CharacterBuildProfile, package: ClassSpellPackage) -> list[CanonicalSpellChoice]:
    choices = [*package.cantrips, *package.spells, *package.always_prepared_spells]
    if profile.class_id == "bard":
        choices.extend(additional_lore_magical_secrets_2014(profile.level))
    return choices


def _spell_issues(profile: CharacterBuildProfile, template: CombatantTemplate) -> list[str]:
    if profile.class_id not in CASTER_CLASS_IDS:
        return []
    if profile.class_id in {"paladin", "ranger"} and profile.level < 2:
        return []
    ability = CASTING_ABILITIES.get(profile.class_id)
    modifier = profile.final_ability_scores.modifier(ability) if ability else None
    package = canonical_spell_package(profile.class_id, profile.level, "2014", modifier)
    if package is None:
        return ["missing-2014-spell-package"]
    runtime_ids = runtime_binding_ids(template)
    issues: list[str] = []
    for spell in _spell_choices(profile, package):
        tags = set(spell.required_capabilities)
        if tags & _NONBLOCKING_SPELL_TAGS:
            continue
        if tags & _UNSUPPORTED_SPELL_TAGS:
            issues.append(f"unsupported-spell:{spell.id}")
            continue
        if not tags:
            issues.append(f"undeclared-spell-capability:{spell.id}")
            continue
        if spell.id not in runtime_ids:
            issues.append(f"unbound-combat-spell:{spell.id}")
    return issues


def _raw_and_engine_issues(
    profile: CharacterBuildProfile,
    template: CombatantTemplate,
    combat_profiles: dict[str, object],
) -> list[str]:
    issues = [*_policy_issues(profile), *audit_character_build(profile, template)]
    if profile.ruleset != "2014" or template.ruleset != "2014":
        issues.append("edition-leak")
    for audit in combat_feature_audits(profile.feature_audits):
        if not audit.automated:
            issues.append(f"unsupported-combat-feature:{audit.feature_id}")
    combat_profile = combat_profiles.get(template.id)
    if combat_profile is None:
        issues.append("missing-combat-fingerprint")
    else:
        issues.extend(audit_pregen_combat_stats(template, combat_profile))
        issues.extend(audit_character_resources(template, profile, combat_profile))
    issues.extend(_spell_issues(profile, template))
    return issues


def audit_2014_pregen_snapshot(
    progression: object,
    level: int,
    combat_profiles: dict[str, object],
) -> Pregen2014SnapshotAudit:
    class_id = getattr(progression, "class_id", "unknown")
    try:
        profile = progression.profile(level)
        template = complete_template_grapple_escape_skills(progression.template_builder(level))
        issues = _raw_and_engine_issues(profile, template, combat_profiles)
        return Pregen2014SnapshotAudit(
            class_id=profile.class_id,
            hero_name=profile.character_name,
            level=profile.level,
            template_id=template.id,
            checked=True,
            passed=not issues,
            unsupported_mechanics=tuple(issues),
        )
    except Exception as exc:
        logger.exception("2014 pregen roster audit failed for %s level %s.", class_id, level)
        return Pregen2014SnapshotAudit(
            class_id=class_id,
            hero_name="",
            level=level,
            template_id="",
            checked=True,
            passed=False,
            unsupported_mechanics=(f"audit-exception:{exc}",),
        )


def audit_2014_pregen_roster() -> list[Pregen2014SnapshotAudit]:
    """Run RAW plus engine-support checks for every registered 2014 pregen snapshot."""
    try:
        combat_profiles = build_all_pregen_combat_profiles()
        rows = [
            audit_2014_pregen_snapshot(progression, level, combat_profiles)
            for progression, level in iter_certified_progression_levels("2014")
        ]
        if len(rows) != EXPECTED_2014_SNAPSHOTS:
            raise RuntimeError(
                f"2014 roster audit expected {EXPECTED_2014_SNAPSHOTS} snapshots, got {len(rows)}."
            )
        return rows
    except Exception:
        logger.exception("Failed to run the 2014 pregen roster audit.")
        raise
