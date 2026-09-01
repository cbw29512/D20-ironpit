from __future__ import annotations

from app.content.pregen_combat_profiles import PregenCombatProfile
from app.domain.models import CombatantTemplate

_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def _proficiency_bonus(level: int) -> int:
    return 2 + (level - 1) // 4


def _expected_saves(profile: PregenCombatProfile) -> dict[str, int]:
    pb = _proficiency_bonus(profile.level)
    proficient = set(profile.save_proficiencies)
    return {
        ability: profile.abilities.modifier(ability) + (pb if ability in proficient else 0)
        for ability in _ABILITIES
    }


def _attack_issues(template: CombatantTemplate, profile: PregenCombatProfile) -> list[str]:
    issues: list[str] = []
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    if len(attacks) != len(profile.attacks):
        return ["attack-count-mismatch"]
    pb = _proficiency_bonus(profile.level)
    for attack, expected in zip(attacks, profile.attacks, strict=True):
        prefix = f"attack:{expected.weapon_id}"
        weapon = attack.weapon
        ability_mod = profile.abilities.modifier(expected.ability)
        if weapon.id != expected.weapon_id:
            issues.append(f"{prefix}:weapon-id-mismatch")
        if (weapon.dice_count, weapon.dice_size, weapon.damage_type.value) != (
            expected.dice_count, expected.dice_size, expected.damage_type,
        ):
            issues.append(f"{prefix}:damage-dice-or-type-mismatch")
        if attack.attack_bonus != ability_mod + pb + expected.style_attack_bonus:
            issues.append(f"{prefix}:attack-bonus-mismatch")
        if attack.damage_bonus != ability_mod:
            issues.append(f"{prefix}:damage-bonus-mismatch")
        if attack.damage_die_minimum != expected.damage_die_minimum:
            issues.append(f"{prefix}:damage-die-minimum-mismatch")
        if weapon.reach_ft != expected.reach_ft:
            issues.append(f"{prefix}:reach-mismatch")
        if (weapon.normal_range_ft, weapon.long_range_ft) != (expected.normal_range_ft, expected.long_range_ft):
            issues.append(f"{prefix}:range-mismatch")
        conditional = tuple(
            (item.dice_count, item.dice_size, item.damage_type.value)
            for item in attack.conditional_damage
        )
        if conditional != expected.conditional_damage:
            issues.append(f"{prefix}:conditional-damage-mismatch")
        if any(item.trigger != "attack_advantage" for item in attack.conditional_damage):
            issues.append(f"{prefix}:conditional-trigger-mismatch")
    return issues


def audit_pregen_combat_stats(template: CombatantTemplate, profile: PregenCombatProfile) -> list[str]:
    issues: list[str] = []
    expected_identity = (profile.template_id, profile.archetype, profile.level)
    if (template.id, template.archetype, template.level) != expected_identity:
        issues.append("identity-or-level-mismatch")
    if template.kind != "character":
        issues.append("kind-mismatch")
    if (template.armor_class, template.max_hp, template.speed_ft) != (
        profile.armor_class, profile.max_hp, profile.speed_ft,
    ):
        issues.append("ac-hp-or-speed-mismatch")
    if template.initiative_bonus != profile.abilities.modifier("dexterity"):
        issues.append("initiative-mismatch")
    if template.saving_throw_bonuses != _expected_saves(profile):
        issues.append("saving-throws-mismatch")
    if template.skill_bonuses != dict(profile.skill_bonuses):
        issues.append("combat-skill-bonuses-mismatch")
    if sorted(template.weapon_masteries) != sorted(profile.weapon_masteries):
        issues.append("weapon-masteries-mismatch")
    if template.fighting_style != profile.fighting_style:
        issues.append("fighting-style-mismatch")
    if template.rage_damage_bonus != profile.rage_damage_bonus:
        issues.append("rage-damage-mismatch")
    resources = {item.id: item.max_uses for item in template.resources}
    if resources != dict(profile.resources):
        issues.append("resources-mismatch")
    if template.damage_resistances or template.damage_vulnerabilities or template.damage_immunities or template.condition_immunities:
        issues.append("unexpected-static-defense-mismatch")
    if not template.source.strip():
        issues.append("source-missing")
    issues.extend(_attack_issues(template, profile))
    return issues


def assert_pregen_combat_stats(template: CombatantTemplate, profile: PregenCombatProfile) -> None:
    issues = audit_pregen_combat_stats(template, profile)
    if issues:
        raise ValueError(f"Pregen combat audit failed for {template.id}: " + ", ".join(issues))
