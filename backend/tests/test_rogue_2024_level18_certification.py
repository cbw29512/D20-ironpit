from __future__ import annotations

from app.combat.conditional_attack_advantage import suppress_attack_advantage_sources
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level18_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level18_profile


def test_2024_rogue_level18_inherits_level17_and_adds_elusive() -> None:
    level17 = build_mara_quickstep_level(17)
    template = build_mara_quickstep_level(18)

    assert unsupported_mara_rogue_features(18) == ()
    assert template.id == "mara-quickstep-l18"
    assert template.level == 18
    assert template.ability_scores is not None
    assert (
        template.ability_scores.dexterity,
        template.ability_scores.constitution,
        template.ability_scores.wisdom,
    ) == (20, 20, 12)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 183, 5)
    assert template.max_hp - level17.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (11, 5)
    assert template.saving_throw_bonuses == {
        "strength": 1, "dexterity": 11, "constitution": 5,
        "intelligence": 6, "wisdom": 7, "charisma": 6,
    }
    assert template.progression_features.sneak_attack_d6 == 9
    assert template.progression_features.attack_advantage_suppressed_unless_incapacitated is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 6
    assert "Rogue 18" in template.source


def test_elusive_suppresses_advantage_only_until_incapacitated() -> None:
    state = build_combatant_state(build_mara_quickstep_level(18))
    assert suppress_attack_advantage_sources(4, state) == 0

    state.is_unconscious = True
    assert suppress_attack_advantage_sources(4, state) == 4


def test_2024_rogue_level18_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level18_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 18
    assert audits["elusive"].combat_relevant is True
    assert audits["elusive"].automated is True

    fingerprint = build_mara_quickstep_level18_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 183, 9)
    assert fingerprint.abilities.wisdom == 12
    assert ("adrenaline-rush", 6) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 18, "canonical")] == ("Mara Quickstep", "mara-quickstep-l18")
