from __future__ import annotations

from app.combat.cunning_strike import resolve_trip
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level9_combat_profile
from app.content.rogue_high_progression_profile import build_mara_quickstep_level9_profile


def test_2024_rogue_level9_is_level8_plus_pb_sneak_and_supreme_sneak_audit() -> None:
    template = build_mara_quickstep_level(9)
    assert unsupported_mara_rogue_features(9) == ()
    assert template.id == "mara-quickstep-l9"
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 16)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 75, 5)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (9, 5)
    assert template.saving_throw_bonuses["dexterity"] == 9
    assert template.skill_bonuses == {"athletics": 5, "acrobatics": 9}
    assert template.progression_features.sneak_attack_d6 == 5
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.uncanny_dodge is True
    assert template.progression_features.evasion is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 4


def test_2024_rogue_level9_pb_updates_cunning_strike_dc() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(9))
    defender = build_combatant_state(build_karnok_stoneward_level(9))
    attacker.feature_last_turn_keys["cunning-strike-trip"] = "9:mara"
    result = resolve_trip(attacker, defender, FixedDiceProvider([1, 1]), "9:mara")
    assert result.save_dc == 17


def test_2024_rogue_level9_profile_audits_supreme_sneak_without_fake_hide() -> None:
    profile = build_mara_quickstep_level9_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["thief-supreme-sneak"].combat_relevant is False
    assert audits["thief-supreme-sneak"].automated is False
    assert "no Hide/Stealth path" in (audits["thief-supreme-sneak"].notes or "")

    fingerprint = build_mara_quickstep_level9_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 75, 5)
    assert ("adrenaline-rush", 4) in fingerprint.resources
    registry = build_certified_hero_registry()
    assert registry[("rogue", 9, "canonical")] == ("Mara Quickstep", "mara-quickstep-l9")
