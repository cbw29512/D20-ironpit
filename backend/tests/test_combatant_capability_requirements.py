from app.content.combatant_capability_requirements import (
    audit_combatant_capability_support,
    combatant_capability_requirements,
)
from app.content.fighter_champion_variant_profiles import build_fighter_champion_variant_profile
from app.content.fighter_champion_variant_runtime import compile_fighter_champion_variant


STATUSES = {
    "great-weapon-fighting": "supported",
    "graze-mastery": "supported",
    "sap-mastery": "supported",
    "vex-mastery": "supported",
    "defense-style": "supported",
    "shield-ac": "supported",
    "archery-style": "supported",
    "nick-mastery": "blocked",
    "two-weapon-fighting": "blocked",
    "slow-mastery": "arena_out_of_scope",
}


def _pair(build_id: str, level: int = 3):
    return (
        build_fighter_champion_variant_profile(build_id, level),
        compile_fighter_champion_variant(build_id, level),
    )


def test_great_weapon_requirements_come_from_style_and_mastered_greatsword() -> None:
    profile, template = _pair("great-weapon")
    assert combatant_capability_requirements(profile, template) == {
        "great-weapon-fighting", "graze-mastery",
    }
    assert audit_combatant_capability_support(profile, template, STATUSES) == []


def test_sword_shield_requirements_come_from_style_shield_and_mastered_longsword() -> None:
    profile, template = _pair("sword-shield")
    assert combatant_capability_requirements(profile, template) == {
        "defense-style", "shield-ac", "sap-mastery",
    }
    assert audit_combatant_capability_support(profile, template, STATUSES) == []


def test_archer_is_blocked_by_actual_mastered_nick_weapon_not_by_build_name() -> None:
    profile, template = _pair("archer")
    requirements = combatant_capability_requirements(profile, template)
    assert requirements == {"archery-style", "slow-mastery", "vex-mastery", "nick-mastery"}
    issues = audit_combatant_capability_support(
        profile, template, STATUSES, arena_ignored=frozenset({"slow-mastery"}),
    )
    assert issues == ["combat-capability-not-supported:nick-mastery:blocked"]


def test_dual_wield_is_blocked_by_twf_and_nick_facts() -> None:
    profile, template = _pair("dual-wield")
    issues = audit_combatant_capability_support(
        profile, template, STATUSES, arena_ignored=frozenset({"slow-mastery"}),
    )
    assert "combat-capability-not-supported:nick-mastery:blocked" in issues
    assert "combat-capability-not-supported:two-weapon-fighting:blocked" in issues


def test_nick_is_skipped_when_character_does_not_master_the_scimitar() -> None:
    profile, template = _pair("archer")
    template = template.model_copy(update={
        "weapon_masteries": [weapon_id for weapon_id in template.weapon_masteries if weapon_id != "scimitar"]
    })
    assert "nick-mastery" not in combatant_capability_requirements(profile, template)


def test_mastery_is_skipped_when_weapon_is_not_on_compiled_attack_list() -> None:
    profile, template = _pair("great-weapon")
    template = template.model_copy(update={"weapon_masteries": [*template.weapon_masteries, "scimitar"]})
    assert "nick-mastery" not in combatant_capability_requirements(profile, template)


def test_arena_exception_must_match_a_capability_actually_present_on_sheet() -> None:
    profile, template = _pair("great-weapon")
    issues = audit_combatant_capability_support(
        profile, template, STATUSES, arena_ignored=frozenset({"slow-mastery"}),
    )
    assert issues == ["arena-ignored-capability-not-present:slow-mastery"]
