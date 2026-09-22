from __future__ import annotations

from app.combat.cunning_strike import resolve_trip
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level10_combat_profile
from app.content.rogue_high_progression_profile import build_mara_quickstep_level10_profile


def test_2024_rogue_level10_is_level9_plus_constitution_asi() -> None:
    template = build_mara_quickstep_level(10)
    assert unsupported_mara_rogue_features(10) == ()
    assert template.id == "mara-quickstep-l10"
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 18)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 93, 5)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (9, 5)
    assert template.saving_throw_bonuses["dexterity"] == 9
    assert template.saving_throw_bonuses["constitution"] == 4
    assert template.skill_bonuses == {"athletics": 5, "acrobatics": 9}
    assert template.progression_features.sneak_attack_d6 == 5
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.uncanny_dodge is True
    assert template.progression_features.evasion is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 4


def test_2024_rogue_level10_keeps_pb4_cunning_strike_dc() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(10))
    defender = build_combatant_state(build_karnok_stoneward_level(10))
    attacker.feature_last_turn_keys["cunning-strike-trip"] = "10:mara"
    result = resolve_trip(attacker, defender, FixedDiceProvider([1]), "10:mara")
    assert result.save_dc == 17


def test_2024_rogue_level10_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level10_profile()
    assert (profile.final_ability_scores.dexterity, profile.final_ability_scores.constitution) == (20, 18)
    increases = [(item.ability, item.amount) for item in profile.advancement_increases]
    assert increases == [
        ("dexterity", 1), ("constitution", 1), ("dexterity", 2), ("constitution", 2),
    ]
    fingerprint = build_mara_quickstep_level10_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 93, 5)
    assert ("adrenaline-rush", 4) in fingerprint.resources
    registry = build_certified_hero_registry()
    assert registry[("rogue", 10, "canonical")] == ("Mara Quickstep", "mara-quickstep-l10")
