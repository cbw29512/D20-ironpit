from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level16_combat_profile
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level16_profile


def test_2024_rogue_level16_inherits_level15_and_applies_wisdom_asi() -> None:
    level15 = build_mara_quickstep_level(15)
    template = build_mara_quickstep_level(16)

    assert unsupported_mara_rogue_features(16) == ()
    assert template.id == "mara-quickstep-l16"
    assert template.level == 16
    assert template.ability_scores is not None
    assert (
        template.ability_scores.dexterity,
        template.ability_scores.constitution,
        template.ability_scores.wisdom,
    ) == (20, 20, 12)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 163, 5)
    assert template.max_hp - level15.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (10, 5)
    assert template.saving_throw_bonuses == {
        "strength": 1,
        "dexterity": 10,
        "constitution": 5,
        "intelligence": 5,
        "wisdom": 6,
        "charisma": 5,
    }
    assert template.progression_features.sneak_attack_d6 == 8
    assert template.progression_features.cunning_strike_obscure_die_cost == 3
    assert template.progression_features.cunning_strike_max_effects == 2
    assert "Rogue 16" in template.source


def test_2024_rogue_level16_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level16_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 16
    assert (profile.final_ability_scores.wisdom, profile.final_ability_scores.dexterity) == (12, 20)
    assert audits["ability-score-improvement-l16"].automated is True
    assert "+2 Wisdom" in " ".join(profile.source_references)

    fingerprint = build_mara_quickstep_level16_combat_profile()
    assert fingerprint.abilities.wisdom == 12
    assert fingerprint.save_proficiencies == ("dexterity", "intelligence", "wisdom", "charisma")
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 163, 8)

    registry = build_certified_hero_registry()
    assert registry[("rogue", 16, "canonical")] == ("Mara Quickstep", "mara-quickstep-l16")
