from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.rogue_progression_profile import build_mara_quickstep_level4_profile
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level4_combat_profile


def test_2024_rogue_level4_applies_canonical_asi_to_all_derived_combat_stats() -> None:
    template = build_mara_quickstep_level(4)
    assert unsupported_mara_rogue_features(4) == ()
    assert template.id == "mara-quickstep-l4"
    assert template.level == 4
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (18, 16)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (15, 35, 4)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (6, 4)
    assert (template.alternate_weapon_attacks[0].attack_bonus, template.alternate_weapon_attacks[0].damage_bonus) == (6, 4)
    assert template.saving_throw_bonuses["dexterity"] == 6
    assert template.saving_throw_bonuses["constitution"] == 3
    assert template.skill_bonuses == {"athletics": 3, "acrobatics": 6}
    assert template.progression_features.sneak_attack_d6 == 2


def test_2024_rogue_level4_profile_records_the_legal_split_asi() -> None:
    profile = build_mara_quickstep_level4_profile()
    assert profile.level == 4
    assert (profile.final_ability_scores.dexterity, profile.final_ability_scores.constitution) == (18, 16)
    increases = [(item.ability, item.amount) for item in profile.advancement_increases]
    assert increases == [("dexterity", 1), ("constitution", 1)]
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l4"].combat_relevant is True
    assert audits["ability-score-improvement-l4"].automated is True


def test_2024_rogue_level4_fingerprint_and_registry_match_runtime() -> None:
    fingerprint = build_mara_quickstep_level4_combat_profile()
    assert (fingerprint.abilities.dexterity, fingerprint.abilities.constitution) == (18, 16)
    assert (fingerprint.armor_class, fingerprint.max_hp) == (15, 35)
    assert fingerprint.sneak_attack_d6 == 2
    registry = build_certified_hero_registry()
    assert registry[("rogue", 4, "canonical")] == ("Mara Quickstep", "mara-quickstep-l4")
