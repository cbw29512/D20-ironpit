from __future__ import annotations

from app.domain.character_builds import AbilityName, CharacterBuildProfile
from app.domain.models import CombatantTemplate

_ABILITIES: tuple[AbilityName, ...] = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)
_REQUIRED_AUDIT_CATEGORIES = {"class", "species", "feat", "equipment"}


def _audit_background_increases(profile: CharacterBuildProfile) -> list[str]:
    issues: list[str] = []
    allowed = set(profile.background_allowed_abilities)
    increases = profile.background_increases
    used = [increase.ability for increase in increases]
    amounts = sorted(increase.amount for increase in increases)

    if len(allowed) != 3:
        issues.append("background-must-list-three-distinct-abilities")
    if len(set(used)) != len(used):
        issues.append("background-increases-must-use-distinct-abilities")
    if not set(used).issubset(allowed):
        issues.append("background-increase-uses-disallowed-ability")
    if amounts not in ([1, 2], [1, 1, 1]):
        issues.append("background-increase-pattern-must-be-plus2-plus1-or-three-plus1")
    return issues


def _audit_final_scores(profile: CharacterBuildProfile) -> list[str]:
    increases = {increase.ability: increase.amount for increase in profile.background_increases}
    issues: list[str] = []
    for ability in _ABILITIES:
        expected = profile.base_ability_scores.score(ability) + increases.get(ability, 0)
        actual = profile.final_ability_scores.score(ability)
        if actual != expected:
            issues.append(f"final-{ability}-does-not-match-background-increases")
        if actual > 20:
            issues.append(f"final-{ability}-exceeds-20")
    return issues


def _audit_features(
    profile: CharacterBuildProfile,
    template: CombatantTemplate,
) -> list[str]:
    issues: list[str] = []
    feature_ids = [audit.feature_id for audit in profile.feature_audits]
    if len(feature_ids) != len(set(feature_ids)):
        issues.append("feature-audit-ids-must-be-unique")
    categories = {audit.category for audit in profile.feature_audits}
    for category in sorted(_REQUIRED_AUDIT_CATEGORIES - categories):
        issues.append(f"missing-{category}-feature-audit")
    if profile.origin_feat_id not in feature_ids:
        issues.append("origin-feat-missing-from-feature-audit")

    runtime_weapon_ids = {
        template.weapon_attack.weapon.id,
        *(attack.weapon.id for attack in template.alternate_weapon_attacks),
    }
    for audit in profile.feature_audits:
        if audit.combat_relevant and not audit.automated:
            issues.append(f"combat-feature-not-automated:{audit.feature_id}")
        required_weapon = audit.runtime_attack_weapon_id
        if required_weapon and required_weapon not in runtime_weapon_ids:
            issues.append(f"runtime-weapon-not-automated:{required_weapon}")
    return issues


def _audit_magic_items(profile: CharacterBuildProfile) -> list[str]:
    issues: list[str] = []
    item_ids = [item.item_id for item in profile.magic_item_audits]
    if len(item_ids) != len(set(item_ids)):
        issues.append("magic-item-audit-ids-must-be-unique")
    for item in profile.magic_item_audits:
        if not item.source_reference.strip():
            issues.append(f"magic-item-source-missing:{item.item_id}")
        if item.combat_relevant and not item.automated:
            issues.append(f"combat-magic-item-not-automated:{item.item_id}")
    return issues


def audit_character_build(
    profile: CharacterBuildProfile,
    template: CombatantTemplate,
) -> list[str]:
    """Return stable fail-closed blockers for a claimed legal 2024 character build."""
    issues: list[str] = []
    if template.kind != "character":
        issues.append("runtime-template-is-not-character")
    if template.id != profile.template_id:
        issues.append("runtime-template-id-mismatch")
    if template.level != profile.level:
        issues.append("runtime-level-mismatch")
    if template.archetype.lower() != profile.class_name.lower():
        issues.append("runtime-class-mismatch")
    if sorted(template.weapon_masteries) != sorted(profile.weapon_masteries):
        issues.append("runtime-weapon-masteries-mismatch")
    if template.fighting_style != profile.fighting_style:
        issues.append("runtime-fighting-style-mismatch")

    issues.extend(_audit_background_increases(profile))
    issues.extend(_audit_final_scores(profile))
    issues.extend(_audit_features(profile, template))
    issues.extend(_audit_magic_items(profile))
    if not profile.source_references or any(not ref.strip() for ref in profile.source_references):
        issues.append("source-reference-missing")
    return issues


def assert_character_build_raw_ready(
    profile: CharacterBuildProfile,
    template: CombatantTemplate,
) -> None:
    issues = audit_character_build(profile, template)
    if issues:
        raise ValueError("Character build is not RAW-ready: " + ", ".join(issues))
