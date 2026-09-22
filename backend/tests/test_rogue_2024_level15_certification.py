from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level15_combat_profile
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level15_profile


def test_2024_rogue_level15_inherits_level14_and_adds_slippery_mind() -> None:
    level14 = build_mara_quickstep_level(14)
    template = build_mara_quickstep_level(15)

    assert unsupported_mara_rogue_features(15) == ()
    assert template.id == "mara-quickstep-l15"
    assert template.level == 15
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 20)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 153, 5)
    assert template.max_hp - level14.max_hp == 10
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (10, 5)
    assert template.saving_throw_bonuses == {
        "strength": 1,
        "dexterity": 10,
        "constitution": 5,
        "intelligence": 5,
        "wisdom": 5,
        "charisma": 5,
    }
    assert template.skill_bonuses == {"athletics": 6, "acrobatics": 10}
    assert template.progression_features.sneak_attack_d6 == 8
    grants = template.progression_features.saving_throw_proficiency_grants
    assert len(grants) == 1
    assert grants[0].source_id == "slippery-mind"
    assert grants[0].abilities == ["wisdom", "charisma"]
    assert template.progression_features.cunning_strike_obscure_die_cost == 3
    assert template.progression_features.cunning_strike_max_effects == 2
    assert "Rogue 15" in template.source


def test_2024_rogue_level15_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level15_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 15
    assert audits["slippery-mind"].combat_relevant is True
    assert audits["slippery-mind"].automated is True

    fingerprint = build_mara_quickstep_level15_combat_profile()
    assert fingerprint.save_proficiencies == ("dexterity", "intelligence", "wisdom", "charisma")
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 153, 8)
    assert ("adrenaline-rush", 5) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 15, "canonical")] == ("Mara Quickstep", "mara-quickstep-l15")
