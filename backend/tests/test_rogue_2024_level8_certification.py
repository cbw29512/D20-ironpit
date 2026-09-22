from __future__ import annotations

from app.combat.cunning_strike import resolve_trip
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level8_combat_profile
from app.content.rogue_mid_progression_profile import build_mara_quickstep_level8_profile


def test_2024_rogue_level8_is_level7_plus_dexterity_asi() -> None:
    template = build_mara_quickstep_level(8)
    assert unsupported_mara_rogue_features(8) == ()
    assert template.id == "mara-quickstep-l8"
    assert template.level == 8
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 16)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 67, 5)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (8, 5)
    assert template.saving_throw_bonuses["dexterity"] == 8
    assert template.skill_bonuses == {"athletics": 4, "acrobatics": 8}
    assert template.progression_features.sneak_attack_d6 == 4
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.uncanny_dodge is True
    assert template.progression_features.evasion is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 3


def test_2024_rogue_level8_asi_updates_cunning_strike_dc() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(8))
    defender = build_combatant_state(build_karnok_stoneward_level(8))
    attacker.feature_last_turn_keys["cunning-strike-trip"] = "8:mara"
    result = resolve_trip(attacker, defender, FixedDiceProvider([1]), "8:mara")
    assert result.save_dc == 16


def test_2024_rogue_level8_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level8_profile()
    assert (profile.final_ability_scores.dexterity, profile.final_ability_scores.constitution) == (20, 16)
    increases = [(item.ability, item.amount) for item in profile.advancement_increases]
    assert increases == [("dexterity", 1), ("constitution", 1), ("dexterity", 2)]
    fingerprint = build_mara_quickstep_level8_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 67, 4)
    registry = build_certified_hero_registry()
    assert registry[("rogue", 8, "canonical")] == ("Mara Quickstep", "mara-quickstep-l8")
