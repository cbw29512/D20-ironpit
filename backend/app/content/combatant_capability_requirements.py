from __future__ import annotations

from collections.abc import Mapping

from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate

_STYLE_REQUIREMENTS = {
    "Archery": "archery-style",
    "Defense": "defense-style",
    "Great Weapon Fighting": "great-weapon-fighting",
    "Two-Weapon Fighting": "two-weapon-fighting",
}
_MASTERY_REQUIREMENTS = {
    "Graze": "graze-mastery",
    "Nick": "nick-mastery",
    "Sap": "sap-mastery",
    "Slow": "slow-mastery",
    "Vex": "vex-mastery",
}


def combatant_capability_requirements(
    profile: CharacterBuildProfile,
    template: CombatantTemplate,
) -> frozenset[str]:
    """Derive shared mechanics only from facts that exist on the compiled character."""
    requirements = {
        _STYLE_REQUIREMENTS[style]
        for style in profile.fighting_styles
        if style in _STYLE_REQUIREMENTS
    }
    if template.visual.off_hand == "shield":
        requirements.add("shield-ac")
    progression = template.progression_features
    replacements = set(progression.tactical_master_sap_weapon_ids)
    if progression.indomitable_bonus:
        requirements.add("indomitable")
    if replacements:
        requirements.add("tactical-master")
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    mastered = set(template.weapon_masteries)
    for attack in attacks:
        weapon = attack.weapon
        if weapon.id not in mastered or weapon.mastery_property is None:
            continue
        if weapon.id in replacements:
            continue
        capability = _MASTERY_REQUIREMENTS.get(weapon.mastery_property)
        if capability is None:
            raise ValueError(f"No capability mapping exists for mastery {weapon.mastery_property!r}.")
        requirements.add(capability)
    return frozenset(requirements)


def audit_combatant_capability_support(
    profile: CharacterBuildProfile,
    template: CombatantTemplate,
    capability_statuses: Mapping[str, str],
    *,
    arena_ignored: frozenset[str] = frozenset(),
) -> list[str]:
    """Fail closed when a mechanic present on the creature lacks certified runtime support."""
    requirements = combatant_capability_requirements(profile, template)
    issues: list[str] = []
    unexpected_ignored = arena_ignored - requirements
    for capability_id in sorted(unexpected_ignored):
        issues.append(f"arena-ignored-capability-not-present:{capability_id}")
    for capability_id in sorted(requirements):
        status = capability_statuses.get(capability_id)
        if capability_id in arena_ignored:
            if status != "arena_out_of_scope":
                issues.append(f"arena-ignored-capability-not-out-of-scope:{capability_id}:{status}")
        elif status != "supported":
            issues.append(f"combat-capability-not-supported:{capability_id}:{status}")
    return issues
