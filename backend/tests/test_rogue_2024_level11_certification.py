from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.sneak_attack import sneak_attack_bonus_damage
from app.combat.cunning_strike import resolve_trip
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level11_combat_profile
from app.content.rogue_high_progression_profile import build_mara_quickstep_level11_profile
from app.domain.models import RollMode


def test_2024_rogue_level11_is_level10_plus_improved_cunning_strike() -> None:
    level10 = build_mara_quickstep_level(10)
    template = build_mara_quickstep_level(11)

    assert unsupported_mara_rogue_features(11) == ()
    assert template.id == "mara-quickstep-l11"
    assert template.level == 11
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 18)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 102, 5)
    assert template.max_hp - level10.max_hp == 9
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (9, 5)
    assert template.saving_throw_bonuses["dexterity"] == 9
    assert template.saving_throw_bonuses["constitution"] == 4
    assert template.skill_bonuses == {"athletics": 5, "acrobatics": 9}
    assert template.progression_features.sneak_attack_d6 == 6
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.cunning_strike_max_effects == 2
    assert template.progression_features.uncanny_dodge is True
    assert template.progression_features.evasion is True
    assert "Rogue 11" in template.source


def test_2024_rogue_level11_canonical_policy_may_legally_use_only_trip() -> None:
    attacker = build_combatant_state(build_mara_quickstep_level(11))
    defender = build_combatant_state(build_karnok_stoneward_level(11))
    attack = attacker.template.weapon_attack
    turn_key = "11:mara"

    spec = sneak_attack_bonus_damage(
        attacker, attack, RollMode.ADVANTAGE, turn_key, False, defender,
    )
    assert spec is not None
    assert spec[1] == 5
    assert attacker.template.progression_features.cunning_strike_max_effects == 2

    trip = resolve_trip(attacker, defender, FixedDiceProvider([1]), turn_key)
    assert trip.save_dc == 17
    assert trip.save_succeeded is False
    assert trip.applied is True


def test_2024_rogue_level11_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level11_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert profile.level == 11
    assert audits["improved-cunning-strike"].combat_relevant is True
    assert audits["improved-cunning-strike"].automated is True

    fingerprint = build_mara_quickstep_level11_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 102, 6)
    assert ("adrenaline-rush", 4) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 11, "canonical")] == ("Mara Quickstep", "mara-quickstep-l11")
