from copy import deepcopy

from app.content.pregen_combat_audit import audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.roster import build_arena_roster


def test_every_arena_pregen_has_a_complete_combat_profile() -> None:
    characters = {item.id: item for item in build_arena_roster().characters}
    profiles = build_pregen_combat_profiles()
    assert set(characters) == set(profiles)
    failures = []
    for template_id, template in characters.items():
        issues = audit_pregen_combat_stats(template, profiles[template_id])
        if issues:
            failures.append(f"{template_id}: {', '.join(issues)}")
    assert failures == [], "Pregen combat stat mismatches:\n" + "\n".join(failures)


def test_every_pregen_exposes_all_six_saves_and_grapple_escape_math() -> None:
    for template in build_arena_roster().characters:
        assert set(template.saving_throw_bonuses) == {
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
        }
        assert "athletics" in template.skill_bonuses
        assert "acrobatics" in template.skill_bonuses


def test_pregen_audit_catches_attack_bonus_and_hp_drift() -> None:
    template = deepcopy(build_arena_roster().characters[0])
    profile = build_pregen_combat_profiles()[template.id]
    template.max_hp += 1
    template.weapon_attack.attack_bonus += 1
    issues = audit_pregen_combat_stats(template, profile)
    assert "ac-hp-or-speed-mismatch" in issues
    assert any(issue.endswith("attack-bonus-mismatch") for issue in issues)
